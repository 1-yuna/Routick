# ─────────────────────────────────────────────────────────────────────
# select_itinerary
# ─────────────────────────────────────────────────────────────────────
# 3-7. 최적 일정 선택
#
# 흐름:
#   1. day별 동선 후보를 LLM 프롬프트로 구성 (start/end/parking 제외, 축약 정보만)
#      후보 1개뿐인 day는 LLM 판단 없이 자동 선택
#   2. LLM 호출 → day별 selected_index, select_reason, compare_reason,
#      recommendation_reasons 획득
#   3. day 간 동일 장소(place_id) 중복 검증
#      - 중복 없음: 통과
#      - 중복 있음: 후보 조합 중 중복 없는 조합 재탐색
#        없으면 중복 장소를 제외 목록(excluded_place_ids)에 추가하고
#        rollback (최대 2회, generate_candidates 재실행 필요 신호 반환)
#   4. 최종 선택된 동선 + 추천 이유를 반영한 itinerary 반환
# ─────────────────────────────────────────────────────────────────────

import os
import json
import itertools
import httpx

from prompts.select_itinerary_prompt import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

MAX_ROLLBACK = 2


# ─── LLM 호출 ───
async def _call_llm(itineraries_by_day: dict, user_input: dict) -> dict:
    prompt = build_prompt(itineraries_by_day, user_input)
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            OPENAI_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        clean = content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


# ─── 일반 장소(place_id) 목록 추출 (start/end/parking 제외) ───
def _place_ids(itinerary: list[dict]) -> set[str]:
    return {
        item["place"]["id"] for item in itinerary
        if item["place"].get("bucket") not in ("start", "end", "parking")
    }


# ─── day 간 동일 장소 중복 여부 확인 ───
def _has_duplicate(selected_by_day: dict[int, list[dict]]) -> bool:
    all_ids: list[str] = []
    for itinerary in selected_by_day.values():
        all_ids.extend(_place_ids(itinerary))
    return len(all_ids) != len(set(all_ids))


# ─── 중복 없는 day 간 조합 재탐색 ───
def _find_non_duplicate_combo(
    itineraries_by_day: dict[int, list[list[dict]]],
) -> dict[int, list[dict]] | None:
    day_numbers = sorted(itineraries_by_day.keys())
    candidate_lists = [itineraries_by_day[d] for d in day_numbers]

    for combo in itertools.product(*candidate_lists):
        all_ids: list[str] = []
        for itinerary in combo:
            all_ids.extend(_place_ids(itinerary))
        if len(all_ids) == len(set(all_ids)):
            return {d: combo[i] for i, d in enumerate(day_numbers)}

    return None


# ─── 중복 장소를 동선에 추천 이유 등 LLM 결과 머지 ───
def _apply_recommendations(itinerary: list[dict], reasons: list[dict]) -> list[dict]:
    reason_map = {str(r["place_id"]): r["reason"] for r in reasons}
    result = []
    for item in itinerary:
        place_id = str(item["place"].get("id", ""))
        if place_id in reason_map and reason_map[place_id]:
            result.append({**item, "recommendation_reason": reason_map[place_id]})
        else:
            # LLM이 해당 장소를 빠뜨린 경우 summary로 fallback
            fallback = item["place"].get("summary", "") or item.get("recommendation_reason", "")
            result.append({**item, "recommendation_reason": fallback})
    return result


# ─── [노드] 최적 일정 선택 ───
async def select_itinerary(state: dict) -> dict:
    ui = state["user_input"]
    itineraries_by_day = state.get("itineraries_by_day", {})
    warnings: list[str] = []

    if not itineraries_by_day:
        return {
            "final_itineraries": {},
            "warnings": ["itineraries_by_day 비어있음"],
            "step": "failed",
        }

    rollback_count = state.get("rollback_count", 0)

    try:
        llm_result = await _call_llm(itineraries_by_day, ui)
    except Exception as e:
        warnings.append(f"LLM 호출 실패: {type(e).__name__}: {e}")
        # fallback: day별 1순위(0번 index) 동선 사용
        llm_result = {
            "days": [
                {
                    "day_number": d,
                    "selected_index": 0,
                    "select_reason": "LLM 호출 실패로 1순위 동선 자동 선택",
                    "compare_reason": "",
                    "recommendation_reasons": [],
                }
                for d in itineraries_by_day.keys()
            ]
        }

    # LLM이 선택한 동선 매핑
    selected_by_day: dict[int, list[dict]] = {}
    day_meta: dict[int, dict] = {}

    for day_result in llm_result.get("days", []):
        day_number = day_result["day_number"]
        # LLM 응답에서 day_number가 문자열 등으로 올 수 있어 int로 명시 변환
        try:
            day_number = int(day_number)
        except (TypeError, ValueError):
            warnings.append(f"day_number 변환 실패, 스킵: {day_result.get('day_number')!r}")
            continue

        idx        = day_result.get("selected_index", 0)
        candidates = itineraries_by_day.get(day_number, [])

        if not candidates:
            continue
        idx = min(idx, len(candidates) - 1)

        itinerary = _apply_recommendations(
            candidates[idx],
            day_result.get("recommendation_reasons", [])
        )
        selected_by_day[day_number] = itinerary
        day_meta[day_number] = {
            "select_reason":  day_result.get("select_reason", ""),
            "compare_reason": day_result.get("compare_reason", ""),
        }

    # ── day 간 중복 검증 ──
    if not _has_duplicate(selected_by_day):
        warnings.append("day 간 중복 없음 → 통과")
        return {
            "final_itineraries": selected_by_day,
            "day_meta":          day_meta,
            "warnings":          warnings,
            "step":              "itinerary_selected",
        }

    warnings.append("day 간 중복 발견 → 조합 재탐색")

    # ── 중복 없는 조합 재탐색 ──
    combo = _find_non_duplicate_combo(itineraries_by_day)
    if combo:
        warnings.append("중복 없는 조합 발견 → 해당 조합 사용 (추천 이유는 LLM 결과 재매핑 불가, 기본값 유지)")
        return {
            "final_itineraries": combo,
            "day_meta":          day_meta,
            "warnings":          warnings,
            "step":              "itinerary_selected",
        }

    # ── rollback ──
    if rollback_count >= MAX_ROLLBACK:
        warnings.append(f"rollback {MAX_ROLLBACK}회 초과 → 실패")
        return {
            "final_itineraries": {},
            "warnings":          warnings,
            "step":              "failed",
        }

    # 중복된 place_id 추출
    seen: set[str] = set()
    duplicated_ids: set[str] = set()
    for itinerary in selected_by_day.values():
        for pid in _place_ids(itinerary):
            if pid in seen:
                duplicated_ids.add(pid)
            seen.add(pid)

    excluded_place_ids = list(set(state.get("excluded_place_ids", [])) | duplicated_ids)
    warnings.append(f"rollback 요청 (시도 {rollback_count + 1}/{MAX_ROLLBACK}), 제외 장소: {excluded_place_ids}")

    return {
        "final_itineraries":  {},
        "warnings":           warnings,
        "step":               "rollback_required",
        "excluded_place_ids": excluded_place_ids,
        "rollback_count":     rollback_count + 1,
    }