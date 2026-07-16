# ─────────────────────────────────────────────────────────────────────
# region_hint
# ─────────────────────────────────────────────────────────────────────
# 3-2. 지역 힌트 조회 (v3 신규)
#
# 흐름:
#   1. day별 힌트 질의용 앵커 지역명 확보
#      - endpoint: mid_name > start_name (프론트에서 받은 값 우선 재사용)
#        둘 다 없으면 center_lat/lng(=mid 좌표)를 카카오 좌표→행정구역 API로 역지오코딩
#      - only: center_lat/lng(=목적지 좌표)를 역지오코딩
#   2. LLM(GPT-4o-mini)에게 그 지역 근처에서 실제로 많이 찾는 구체적 장소·거리명 힌트 요청
#      (카테고리성 표현 대신 구체적 상호명만 추출하도록 프롬프트에서 강제)
#      *(v3.1)* travel_mode(도보/자동차) + route_type을 프롬프트에 포함
#      - 자동차 + only: 가까운 곳 최우선, 부족할 때만 차로 20~30분 내로 보충
#      - 그 외 (도보, 또는 endpoint): 지역 바로 근처에 몰려 있는 장소만
#        (endpoint는 day별 mid가 중심이라 다른 day 지역과 힌트가 섞이면 안 됨)
#   3. day별 hint_keywords로 저장
#      *(v3.1)* 힌트는 collect_pool에서 수집의 앵커(중심점)로 사용됨:
#      앵커 해소 → 앵커 주변 소반경 수집(메인) → 조건부 center 보충 수집(폴백)
#      이후 first_filter(정렬 우선순위)·second_filter(점수 보너스)에서도 활용
#   4. 앵커 지역명 확보 실패 / LLM 호출 실패 / 빈 응답이어도 hint_keywords=[]로 폴백,
#      collect_pool은 기존 center 반경 검색만으로 진행 (파이프라인 블로킹 없음)
# ─────────────────────────────────────────────────────────────────────

import json
import os
import httpx

from utils.pool.kakao_search import coord_to_region
from prompts.region_hint_prompt import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

MAX_HINTS_PER_DAY = 5


# ─── day별 힌트 질의용 앵커 지역명 확보 ───
async def _anchor_name(
    client:   httpx.AsyncClient,
    day_info: dict,
    day_raw:  dict | None,
) -> str:
    if day_raw:
        if day_raw.get("mid_name"):
            return day_raw["mid_name"]
        if day_raw.get("start_name"):
            return day_raw["start_name"]

    lat = day_info.get("center_lat")
    lng = day_info.get("center_lng")
    if lat is None or lng is None:
        return ""
    return await coord_to_region(client, lat, lng)


# ─── LLM 힌트 질의 ───
async def _call_llm(
    client:        httpx.AsyncClient,
    region_name:   str,
    moods_kr:      list[str],
    activities_kr: list[str],
    transport:     str,
    route_type:    str,
) -> list[str]:
    prompt = build_prompt(region_name, moods_kr, activities_kr, transport, route_type)
    try:
        resp = await client.post(
            OPENAI_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        clean   = content.replace("```json", "").replace("```", "").strip()
        data    = json.loads(clean)
        places  = data.get("places", [])
        hints   = [p.strip() for p in places if isinstance(p, str) and p.strip()]
        return hints[:MAX_HINTS_PER_DAY]
    except Exception:
        # LLM 호출/파싱 실패 시 조용히 빈 힌트로 폴백 (파이프라인 블로킹 없음)
        return []


# ─── [노드] 지역 힌트 조회 ───
async def region_hint(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    days_info     = ui.get("days_info") or []
    days_raw      = ui.get("days") or []
    moods_kr      = ui.get("moods_kr") or []
    activities_kr = ui.get("activities_kr") or []
    transport     = ui.get("transport", "walk")   # walk / car *(v3.1)*
    route_type    = ui.get("route_type", "only")  # only / endpoint *(v3.1)*

    if not days_info:
        warnings.append("days_info 없음 → region_hint 스킵")
        return {"user_input": ui, "warnings": warnings, "step": "hint_skipped"}

    hint_keywords_by_day: dict[int, list[str]] = {}

    async with httpx.AsyncClient(timeout=15.0) as client:
        for day_info in days_info:
            day_number = day_info["day_number"]
            day_raw = next((d for d in days_raw if d.get("day_number") == day_number), None)

            region_name = await _anchor_name(client, day_info, day_raw)
            if not region_name:
                warnings.append(f"day{day_number} 힌트 앵커 지역명 확보 실패 → 힌트 스킵")
                hint_keywords_by_day[day_number] = []
                continue

            hints = await _call_llm(client, region_name, moods_kr, activities_kr, transport, route_type)
            hint_keywords_by_day[day_number] = hints

            if hints:
                warnings.append(f"day{day_number} 힌트({region_name}): {hints}")
            else:
                warnings.append(f"day{day_number} 힌트({region_name}) 없음")

    updated_days_info = [
        {**d, "hint_keywords": hint_keywords_by_day.get(d["day_number"], [])}
        for d in days_info
    ]
    ui = {**ui, "days_info": updated_days_info}

    return {
        "user_input": ui,
        "warnings":   warnings,
        "step":       "hint_collected",
    }