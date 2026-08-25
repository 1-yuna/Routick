# ─────────────────────────────────────────────────────────────────────
# 6. select_itinerary
# ─────────────────────────────────────────────────────────────────────
# 최적 일정 선택 노드
#
# 흐름:
#   1. GPT 요청 전 검증 (utils/itinerary_select/validate_routes.py)
#      - 전체 여행 시간 안에 일정 완료 / 장소·브랜드 중복 없음 /
#        카테고리 순서 충족 / 앵커 최소 1개 포함
#      - day별로 검증 통과 동선만 남김
#      - 어떤 day가 검증 통과 동선 0개면: 그 day만 조건 완화해서 롤백 재생성
#        (utils/itinerary_select/regenerate_routes.py — quota 20→30, 6→5슬롯,
#         검증에서 걸린 장소 제외. 블로그/GPT 재호출 없이 이미 계산된
#         scored_by_day에서 quota만 다시 잘라 씀)
#      - 롤백 후에도 0개면 그 day는 제외하고 진행 + 경고
#   2. GPT 요청 — day별 후보를 한 번에 모두 보여주고 day별 최적 동선 1개씩 선택
#      (utils/select_itinerary_prompt.py) — day 간 동일 장소 중복 회피가
#      최우선 기준이라 day를 따로따로 판단하면 안 되므로 단일 호출
#   3. GPT 실패/응답에 day 간 중복 존재: 폴백
#      (utils/itinerary_select/auto_fallback.py) — 중복 없는 후보 조합 중
#      우선순위(총점 합) 최고 조합 자동 선택
# ─────────────────────────────────────────────────────────────────────

import json
import os

import httpx

from prompts.select_itinerary_prompt import build_prompt
from utils.itinerary_select.validate_routes import validate_day_routes, trip_budget_minutes
from utils.itinerary_select.regenerate_routes import regenerate_day
from utils.itinerary_select.auto_fallback import pick_best_combo

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# day 여러 개 + 동선 여러 개를 한 번에 보고 분위기/활동 매칭·구성 다양성·day 간 중복까지
# 종합 판단해야 하는 다기준 추론 작업이라, 단순 분류 작업인 enrich 노드와 달리
# gpt-5.1(추론 강함) 사용 — 다만 호출 빈도가 낮은(day 1묶음, 1회) 노드라 비용 부담은 적음
SELECT_MODEL = "gpt-5.1"


# ─── LLM 호출 ───
async def _call_llm(valid_routes_by_day: dict, ui: dict) -> dict:
    prompt = build_prompt(valid_routes_by_day, ui)
    is_reasoning_model = SELECT_MODEL.startswith(("gpt-5", "o1", "o3", "o4"))
    payload = {
        "model": SELECT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 3000 if is_reasoning_model else 1500,
    }
    if is_reasoning_model:
        payload["reasoning_effort"] = "none" if SELECT_MODEL == "gpt-5.1" else "minimal"
    else:
        payload["temperature"] = 0.3

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            OPENAI_API_URL,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        clean = content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


# ─── GPT가 못 채웠거나(fallback 경로) 응답에서 빠뜨린 장소용 — 점수/분위기·활동 매칭
#     정보로 대신 만드는 추천 이유 (place 블록 description에 그대로 노출됨) ───
def _fallback_place_reason(place: dict) -> str:
    parts = []
    atmosphere = place.get("atmosphere") or []
    if atmosphere:
        parts.append("/".join(atmosphere[:2]) + " 분위기")
    matched = place.get("matched_activities") or []
    if matched:
        parts.append("/".join(matched[:2]) + " 활동과 매칭")
    if place.get("query_name"):
        parts.append("앵커 장소")
    base = ", ".join(parts) if parts else (place.get("summary") or "")
    score = place.get("total_score", 0)
    return f"{base} (적합도 {score}점으로 자동 선택)" if base else f"적합도 {score}점으로 자동 선택"


# ─── route의 각 place에 추천 이유를 부착한 새 route dict 반환 (원본 불변) ───
def _attach_place_reasons(route: dict, reasons: dict[str, str]) -> dict:
    places = [
        {**p, "recommendation_reason": reasons.get(p["id"]) or _fallback_place_reason(p)}
        for p in route["places"]
    ]
    return {**route, "places": places}


# ─── LLM 응답을 day별 선택 동선으로 매핑 — 모든 day가 커버 안 되면 예외(폴백 유도) ───
def _apply_llm_selection(llm_result: dict, valid_routes_by_day: dict) -> tuple[dict, dict]:
    selected_by_day: dict[int, dict] = {}
    day_meta: dict[int, dict] = {}

    for day_result in llm_result.get("days", []):
        day_number = int(day_result["day_number"])
        candidates = valid_routes_by_day.get(day_number)
        if not candidates:
            continue
        idx = day_result.get("selected_route_index", 0)
        idx = min(max(int(idx), 0), len(candidates) - 1)
        route = candidates[idx]

        place_reasons = {
            pr["place_id"]: pr.get("reason", "")
            for pr in (day_result.get("place_reasons") or [])
            if pr.get("place_id")
        }
        selected_by_day[day_number] = _attach_place_reasons(route, place_reasons)
        day_meta[day_number] = {"select_reason": day_result.get("select_reason", "")}

    if set(selected_by_day.keys()) != set(valid_routes_by_day.keys()):
        raise ValueError("LLM 응답이 일부 day를 누락함")

    return selected_by_day, day_meta


# ─── day 간 동일 장소(id) 중복 여부 ───
def _has_duplicate(selected_by_day: dict) -> bool:
    all_ids: list[str] = []
    for route in selected_by_day.values():
        all_ids.extend(p["id"] for p in route["places"])
    return len(all_ids) != len(set(all_ids))


# ─── [노드] 최적 일정 선택 ───
async def select_itinerary(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    route_candidates_by_day = state.get("route_candidates_by_day") or {}
    scored_by_day = state.get("scored_by_day") or {}
    days_info = ui.get("days_info") or []
    day_info_map = {d["day_number"]: d for d in days_info}
    transport  = ui.get("transport", "walk")
    route_type = ui.get("route_type", "only")

    if not route_candidates_by_day and not days_info:
        return {
            "final_itineraries": {},
            "day_meta":          {},
            "user_input":        ui,
            "warnings":          warnings + ["route_candidates_by_day 없음 — generate_route_candidates 점검 필요"],
            "step":              "select_failed",
        }

    budget_minutes = trip_budget_minutes(ui)

    # ── 1. GPT 요청 전 검증 + 필요 시 day별 롤백 재생성 ──
    # route_candidates_by_day.items()가 아니라 요청한 day_number 전체(days_info 기준)를
    # 순회 — generate_route_candidates가 어떤 day를 아예 빠뜨렸어도(요청한 day에 후보 자체가
    # 없는 경우) "요청한 모든 날짜에 동선 후보가 존재" 검증에 걸리도록
    requested_days = sorted(day_info_map.keys()) or sorted(route_candidates_by_day.keys())
    valid_by_day: dict[int, list[dict]] = {}
    for day_number in requested_days:
        routes = route_candidates_by_day.get(day_number, [])
        if day_number not in route_candidates_by_day:
            warnings.append(f"day{day_number} 동선 후보 자체가 없음 (generate_route_candidates 미생성) → 롤백 재생성 시도")

        valid, reasons, failed_ids = validate_day_routes(routes, budget_minutes)

        if not valid:
            warnings.append(f"day{day_number} 사전 검증 통과 동선 0개 (사유: {reasons}) → 롤백 재생성 시도")
            regen_routes, regen_warnings = regenerate_day(
                day_number, scored_by_day.get(day_number, []), failed_ids,
                day_info_map.get(day_number, {}), transport, route_type, budget_minutes,
            )
            warnings.extend(regen_warnings)
            valid = regen_routes

        valid_by_day[day_number] = valid

    failed_days = [d for d, routes in valid_by_day.items() if not routes]
    if failed_days:
        warnings.append(f"day {failed_days} 롤백 후에도 유효 동선 없음 → 해당 day 제외")
        valid_by_day = {d: r for d, r in valid_by_day.items() if r}

    if not valid_by_day:
        return {
            "final_itineraries": {},
            "day_meta":          {},
            "user_input":        ui,
            "warnings":          warnings + ["모든 day 유효 동선 없음"],
            "step":              "select_failed",
        }

    # ── 2. GPT 요청 (day 전체를 한 번에 판단) ──
    selected_by_day: dict[int, dict] | None = None
    day_meta: dict[int, dict] = {}

    try:
        llm_result = await _call_llm(valid_by_day, ui)
        selected_by_day, day_meta = _apply_llm_selection(llm_result, valid_by_day)
        if _has_duplicate(selected_by_day):
            warnings.append("GPT 선택 결과에 day 간 중복 존재 → 폴백")
            selected_by_day = None
        else:
            warnings.append("GPT 선택 완료, day 간 중복 없음")
    except Exception as e:
        warnings.append(f"GPT 선택 실패({type(e).__name__}: {e}) → 폴백")
        selected_by_day = None

    # ── 3. 폴백: 중복 없는 조합 중 우선순위(총점 합) 최고 조합 자동 선택 ──
    if selected_by_day is None:
        combo = pick_best_combo(valid_by_day)
        if combo is None:
            return {
                "final_itineraries": {},
                "day_meta":          {},
                "user_input":        ui,
                "warnings":          warnings + ["폴백 조합 탐색 실패 — day 간 중복 없는 조합이 존재하지 않음"],
                "step":              "select_failed",
            }
        selected_by_day = {d: _attach_place_reasons(route, {}) for d, route in combo.items()}
        day_meta = {d: {"select_reason": "자동 선택 (day 간 중복 없는 조합 중 적합도 총점 최고)"} for d in combo}

    return {
        "final_itineraries": selected_by_day,
        "day_meta":          day_meta,
        "user_input":        ui,
        "warnings":          warnings,
        "step":              "itinerary_selected",
    }