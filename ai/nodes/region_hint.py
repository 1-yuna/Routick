# ─────────────────────────────────────────────────────────────────────
# region_hint
# ─────────────────────────────────────────────────────────────────────
# 여행 권역 조회 노드
#
# 흐름:
#   1. day별 기준 지역명 + 기준 좌표 확보 (day별 병렬)
#      - only: destination, 없으면 lat/lng 역지오코딩
#      - endpoint: mid_name > start_name, 없으면 mid 좌표 역지오코딩
#        mid 좌표 자체가 없으면 start~end 직선 중간점으로 계산
#   2. LLM에게 그 지역 기준으로 하루 콘셉트/선정 이유/앵커 이름 2~3개 요청 (day별 병렬)
#      (region_name은 별도로 만들지 않고 기준 지역명을 그대로 사용)
#   3. 앵커 이름의 place_id/좌표 해소는 여기서 하지 않음 — 다음 노드
#      (collect_and_filter_places)에서 실제 수집과 함께 처리
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
import os
import httpx

from prompts.region_hint_prompt import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_GEO     = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"

REGION_HINT_MODEL = "gpt-5.1"


# ─── 좌표 → 행정구역명 변환 ───
async def coord_to_region(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
) -> str:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {"x": lng, "y": lat}
    try:
        resp = await client.get(KAKAO_GEO, headers=headers, params=params)
        resp.raise_for_status()
        docs = resp.json().get("documents", [])
        for doc in docs:
            if doc.get("region_type") == "H":
                return doc.get("region_2depth_name", "")
        if docs:
            return docs[0].get("region_2depth_name", "")
    except Exception:
        pass
    return ""


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
        # "none"은 gpt-5.1 전용, 그 외 gpt-5 계열(mini/nano 포함)은 "minimal"이 최저 단계
        payload["reasoning_effort"] = "none" if REGION_HINT_MODEL == "gpt-5.1" else "minimal"
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


def _fallback_day(
    day_number: int,
    context_name: str,
    center_lat, center_lng,
    start_lat=None, start_lng=None,
    end_lat=None, end_lng=None,
) -> dict:
    return {
        "day_number":     day_number,
        "region_name":    context_name,
        "region_concept": None,
        "region_reason":  None,
        "anchor_names":   [],
        "center_lat":     center_lat,
        "center_lng":     center_lng,
        "start_lat":      start_lat,
        "start_lng":      start_lng,
        "end_lat":        end_lat,
        "end_lng":        end_lng,
        "is_fallback":    True,
    }


# ─── day 하나 처리: 기준 좌표 확보 실패/LLM 실패 시 폴백 ───
# start/end 좌표는 route_type=endpoint일 때만 존재 — 동선 생성 노드가 출발/도착 블록을
# 붙일 때 쓰므로, mid(center)와 별개로 days_info에 그대로 실어 보냄
async def _process_day(
    client: httpx.AsyncClient,
    day_number: int,
    context_name: str,
    center_lat: float | None,
    center_lng: float | None,
    moods_kr: list[str],
    activities_kr: list[str],
    start_lat: float | None = None,
    start_lng: float | None = None,
    end_lat: float | None = None,
    end_lng: float | None = None,
) -> tuple[dict, str]:
    if not context_name or center_lat is None or center_lng is None:
        return (
            _fallback_day(day_number, context_name, center_lat, center_lng, start_lat, start_lng, end_lat, end_lng),
            f"day{day_number} 기준 지역명/좌표 확보 실패 → 반경 검색 폴백",
        )

    try:
        llm_result = await _call_llm(client, context_name, moods_kr, activities_kr, [])
    except Exception as e:
        return (
            _fallback_day(day_number, context_name, center_lat, center_lng, start_lat, start_lng, end_lat, end_lng),
            f"day{day_number} 권역 조회 LLM 실패: {type(e).__name__} → 반경 검색 폴백",
        )

    anchor_names = [a for a in (llm_result.get("anchors") or []) if isinstance(a, str) and a.strip()]
    day_entry = {
        "day_number":     day_number,
        "region_name":    context_name,
        "region_concept": llm_result.get("concept"),
        "region_reason":  llm_result.get("reason"),
        "anchor_names":   anchor_names,
        "center_lat":     center_lat,
        "center_lng":     center_lng,
        "start_lat":      start_lat,
        "start_lng":      start_lng,
        "end_lat":        end_lat,
        "end_lng":        end_lng,
        "is_fallback":    False,
    }
    return day_entry, f"day{day_number} 권역: {context_name} / 앵커 제안 {len(anchor_names)}개"


# ─── [노드] 여행 권역 조회 ───
async def region_hint(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    route_type    = ui.get("route_type", "only")
    travel_days   = ui.get("travel_days", 1)
    moods_kr      = ui.get("moods_kr") or []
    activities_kr = ui.get("activities_kr") or []
    destination   = ui.get("destination") or ""
    lat           = ui.get("lat")
    lng           = ui.get("lng")
    days_raw      = ui.get("days") or []

    if route_type == "only":
        day_numbers = list(range(1, travel_days + 1))
    else:
        day_numbers = [d["day_number"] for d in days_raw]

    async with httpx.AsyncClient(timeout=30.0) as client:
        bases = await asyncio.gather(*[
            _day_base(
                client,
                next((d for d in days_raw if d.get("day_number") == day_number), None),
                destination, lat, lng,
            )
            for day_number in day_numbers
        ])

        day_raw_map = {d["day_number"]: d for d in days_raw}
        results = await asyncio.gather(*[
            _process_day(
                client, day_number, context_name, center_lat, center_lng, moods_kr, activities_kr,
                start_lat=day_raw_map[day_number]["start_lat"] if day_number in day_raw_map else None,
                start_lng=day_raw_map[day_number]["start_lng"] if day_number in day_raw_map else None,
                end_lat=day_raw_map[day_number]["end_lat"] if day_number in day_raw_map else None,
                end_lng=day_raw_map[day_number]["end_lng"] if day_number in day_raw_map else None,
            )
            for day_number, (context_name, center_lat, center_lng) in zip(day_numbers, bases)
        ])

    days_info = [entry for entry, _ in results]
    warnings.extend(msg for _, msg in results)

    ui = {**ui, "days_info": days_info}

    return {
        "user_input": ui,
        "warnings":   warnings,
        "step":       "region_selected",
    }