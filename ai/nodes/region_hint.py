# ─────────────────────────────────────────────────────────────────────
# region_hint
# ─────────────────────────────────────────────────────────────────────
# 여행 권역 조회 노드
#
# 흐름:
#   1. day별 기준 지역명 + 기준 좌표 확보
#      - only: destination, 없으면 lat/lng 역지오코딩
#      - endpoint: mid_name > start_name, 없으면 mid 좌표 역지오코딩
#        mid 좌표 자체가 없으면 start~end 직선 중간점으로 계산
#   2. LLM에게 그 지역 기준으로 하루 콘셉트/선정 이유/앵커 2~3개 요청
#      (region_name은 별도로 만들지 않고 기준 지역명을 그대로 사용)
#      이전 day에서 이미 쓴 앵커는 avoid 목록으로 넘겨서 중복 방지
#   3. 앵커 이름을 기준 좌표 기준으로 카카오 키워드 검색해 place_id/좌표까지 해소
#      이미 다른 day가 쓴 place_id는 제외
#   4. 앵커가 하나도 안 해소되면 그 day는 폴백 처리
#      (기준 좌표만 남기고 anchors는 비움 → 장소수집에서 반경 검색)
# ─────────────────────────────────────────────────────────────────────

import json
import os
import re
import httpx

from utils.pool.kakao_search import coord_to_region, kakao_keyword_search_radius, parse_kakao_doc
from constants.mapping import BASE_COLLECT_RADIUS_KM
from prompts.region_hint_prompt import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

REGION_HINT_MODEL = "gpt-5.1"

MAX_ANCHORS = 3


# ─── 두 좌표의 직선 중간점 ───
def _midpoint(lat1: float, lng1: float, lat2: float, lng2: float) -> tuple[float, float]:
    return (lat1 + lat2) / 2, (lng1 + lng2) / 2


# ─── day 기준 지역명 + 기준 좌표 확보 ───
async def _day_base(
    client: httpx.AsyncClient,
    day_raw: dict | None,
    destination: str,
    lat: float | None,
    lng: float | None,
) -> tuple[str, float | None, float | None]:
    if day_raw:
        mid_lat = day_raw.get("mid_lat")
        mid_lng = day_raw.get("mid_lng")
        if mid_lat is None or mid_lng is None:
            mid_lat, mid_lng = _midpoint(
                day_raw["start_lat"], day_raw["start_lng"],
                day_raw["end_lat"], day_raw["end_lng"],
            )
        name = day_raw.get("mid_name") or day_raw.get("start_name")
        if not name:
            name = await coord_to_region(client, mid_lat, mid_lng)
        return name, mid_lat, mid_lng

    if destination:
        return destination, lat, lng
    if lat is None or lng is None:
        return "", lat, lng
    name = await coord_to_region(client, lat, lng)
    return name, lat, lng


# ─── LLM 호출 ───
async def _call_llm(
    client: httpx.AsyncClient,
    context_name: str,
    moods_kr: list[str],
    activities_kr: list[str],
    avoid_anchors: list[str],
) -> dict:
    prompt = build_prompt(context_name, moods_kr, activities_kr, avoid_anchors)
    is_reasoning_model = REGION_HINT_MODEL.startswith(("gpt-5", "o1", "o3", "o4"))
    payload = {
        "model": REGION_HINT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 1500 if is_reasoning_model else 500,
    }
    if is_reasoning_model:
        payload["reasoning_effort"] = "low"
    else:
        payload["temperature"] = 0.3
    resp = await client.post(
        OPENAI_API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json=payload,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ─── 앵커 이름 → place_id/좌표 해소 ───
async def _resolve_anchors(
    client: httpx.AsyncClient,
    anchor_names: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    avoid_place_ids: set[str],
) -> list[dict]:
    radius_m = min(int(radius_km * 1000), 20000)
    resolved = []
    for name in anchor_names[:MAX_ANCHORS]:
        try:
            docs = await kakao_keyword_search_radius(client, name, lat, lng, radius_m, page=1)
        except Exception:
            continue
        if not docs:
            stripped = re.sub(r"\s*\([^)]*\)", "", name).strip()
            if not stripped or stripped == name:
                continue
            try:
                docs = await kakao_keyword_search_radius(client, stripped, lat, lng, radius_m, page=1)
            except Exception:
                continue
            if not docs:
                continue
        place = parse_kakao_doc(docs[0])
        if place["id"] in avoid_place_ids:
            continue
        resolved.append({
            "name":       place["name"],
            "query_name": name,
            "place_id":   place["id"],
            "lat":        place["lat"],
            "lng":        place["lng"],
        })
    return resolved


def _fallback_day(
    day_number: int,
    context_name: str,
    center_lat, center_lng,
    llm_result: dict | None = None,
) -> dict:
    return {
        "day_number":     day_number,
        "region_name":    context_name,
        "region_concept": (llm_result or {}).get("concept"),
        "region_reason":  (llm_result or {}).get("reason"),
        "anchors":        [],
        "center_lat":     center_lat,
        "center_lng":     center_lng,
        "is_fallback":    True,
    }


# ─── [노드] 여행 권역 조회 ───
async def region_hint(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    route_type    = ui.get("route_type", "only")
    travel_days   = ui.get("travel_days", 1)
    transport     = ui.get("transport", "walk")
    moods_kr      = ui.get("moods_kr") or []
    activities_kr = ui.get("activities_kr") or []
    destination   = ui.get("destination") or ""
    lat           = ui.get("lat")
    lng           = ui.get("lng")
    days_raw      = ui.get("days") or []

    radius_km = BASE_COLLECT_RADIUS_KM.get(transport, BASE_COLLECT_RADIUS_KM["walk"])

    if route_type == "only":
        day_numbers = list(range(1, travel_days + 1))
    else:
        day_numbers = [d["day_number"] for d in days_raw]

    days_info: list[dict] = []
    used_anchor_names: set[str] = set()
    used_place_ids: set[str] = set()

    async with httpx.AsyncClient(timeout=15.0) as client:
        for day_number in day_numbers:
            day_raw = next((d for d in days_raw if d.get("day_number") == day_number), None)
            context_name, center_lat, center_lng = await _day_base(client, day_raw, destination, lat, lng)

            if not context_name or center_lat is None or center_lng is None:
                warnings.append(f"day{day_number} 기준 지역명/좌표 확보 실패 → 반경 검색 폴백")
                days_info.append(_fallback_day(day_number, context_name, center_lat, center_lng))
                continue

            try:
                llm_result = await _call_llm(
                    client, context_name, moods_kr, activities_kr,
                    list(used_anchor_names),
                )
            except Exception as e:
                warnings.append(f"day{day_number} 권역 조회 LLM 실패: {type(e).__name__} → 반경 검색 폴백")
                days_info.append(_fallback_day(day_number, context_name, center_lat, center_lng))
                continue

            anchor_names = [a for a in (llm_result.get("anchors") or []) if isinstance(a, str) and a.strip()]
            anchors = await _resolve_anchors(client, anchor_names, center_lat, center_lng, radius_km, used_place_ids)

            if not anchors:
                warnings.append(f"day{day_number} 앵커 해소 0개 (LLM 제안: {anchor_names}) → 반경 검색 폴백")
                days_info.append(_fallback_day(day_number, context_name, center_lat, center_lng, llm_result))
                continue

            if len(anchors) < len(anchor_names):
                resolved_query_names = {a["query_name"] for a in anchors}
                dropped = [n for n in anchor_names if n not in resolved_query_names]
                warnings.append(f"day{day_number} 앵커 일부 해소 실패: {dropped}")

            for a in anchors:
                used_anchor_names.add(a["name"])
                used_place_ids.add(a["place_id"])
                if a["name"] != a["query_name"]:
                    warnings.append(f"day{day_number} 앵커 이름 불일치: '{a['query_name']}' 요청 → '{a['name']}' 매칭됨")

            days_info.append({
                "day_number":     day_number,
                "region_name":    context_name,
                "region_concept": llm_result.get("concept"),
                "region_reason":  llm_result.get("reason"),
                "anchors":        anchors,
                "center_lat":     center_lat,
                "center_lng":     center_lng,
                "is_fallback":    False,
            })
            warnings.append(f"day{day_number} 권역: {context_name} / 앵커 {len(anchors)}개")

    ui = {**ui, "days_info": days_info}

    return {
        "user_input": ui,
        "warnings":   warnings,
        "step":       "region_selected",
    }