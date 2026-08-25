# ─────────────────────────────────────────────────────────────────────
# collect_and_filter_places
# ─────────────────────────────────────────────────────────────────────
# 장소 수집 + 1차 필터링 노드
#
# 흐름:
#   1. 앵커 이름 해소 (utils/collect_filter/anchor_resolve.py)
#      - region_hint가 넘긴 anchor_names → place_id/좌표/카테고리
#      - 기준 좌표 주변 카카오 키워드 검색, 괄호 부가설명 있으면 벗겨서 재시도
#      - 이미 다른 day에서 해소된 place_id는 제외 (day 순서대로 누적)
#   2. 하루 당 장소 수집 (utils/collect_filter/day_collect.py)
#      - 기준 지역 주변 장소 수집 (도보 5km / 자동차 10km)
#      - 앵커 주변 장소 추가 수집 (앵커 place_id가 존재 시, 도보 0.8km / 자동차 2km)
#      - place_id 기준 중복 제거
#      - 수집 결과(필터링 전 원본)를 PostgreSQL에 upsert
#   3. 1차 필터링 (utils/collect_filter/day_filter.py)
#      - 제거: 이전 day에서 이미 채택된 장소 (day 간 중복 방지, day 순서대로 누적)
#        / 사용자 제외활동 / 여행과 무관한 키워드 / 동일 이름(접미어 무시)·좌표 중복
#        / 동일 브랜드 하루당 최대 1개 / 동일 세부 카테고리(3단계 이상 일치) 하루당 최대 2개
#      - 카페·베이커리 재분류 (other는 activity로 통합)
#      - 앵커 필수 포함 (제거 단계에서 빠졌으면 다시 추가, 단 제외활동에 걸린 경우는 제외)
#      - 하루 당 30개로 축약 (음식점 10 / 카페·베이커리 5 / 활동·관광 15)
# ─────────────────────────────────────────────────────────────────────

import httpx

from utils.collect_filter.anchor_resolve import resolve_anchors
from utils.collect_filter.day_collect import collect_day_places
from utils.collect_filter.day_filter import filter_day
from constants.mapping import BASE_COLLECT_RADIUS_KM


# ─── [노드] 장소 수집 + 1차 필터링 ───
async def collect_and_filter_places(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    transport         = ui.get("transport", "walk")
    avoid_activities  = ui.get("avoid_activities") or []
    keywords          = ui.get("final_keywords") or []
    days_info         = ui.get("days_info") or []

    if not keywords:
        warnings.append("final_keywords 비어있음 → 기본 키워드 사용")
        keywords = ["맛집", "카페"]

    if not days_info:
        return {
            "filtered_candidates": [],
            "filtered_by_day":     {},
            "user_input":          ui,
            "warnings":            warnings + ["days_info 없음 — region_hint 점검 필요"],
            "step":                "filter_failed",
        }

    radius_km = BASE_COLLECT_RADIUS_KM.get(transport, BASE_COLLECT_RADIUS_KM["walk"])

    filtered_by_day: dict[int, list] = {}
    all_filtered:    list[dict]      = []
    used_place_ids:  set[str]        = set()

    async with httpx.AsyncClient(timeout=15.0) as client:
        for day_info in days_info:
            day_number   = day_info["day_number"]
            center_lat   = day_info.get("center_lat")
            center_lng   = day_info.get("center_lng")
            anchor_names = day_info.get("anchor_names") or []

            if center_lat is None or center_lng is None:
                warnings.append(f"day{day_number} 좌표 없음 → 스킵")
                filtered_by_day[day_number] = []
                continue

            anchors = await resolve_anchors(
                client, anchor_names, center_lat, center_lng, radius_km, used_place_ids,
            )
            if len(anchors) < len(anchor_names):
                resolved_query_names = {a["query_name"] for a in anchors}
                dropped = [n for n in anchor_names if n not in resolved_query_names]
                warnings.append(f"day{day_number} 앵커 일부 해소 실패: {dropped}")
            for a in anchors:
                if a["name"] != a["query_name"]:
                    warnings.append(f"day{day_number} 앵커 이름 불일치: '{a['query_name']}' 요청 → '{a['name']}' 매칭됨")

            places = await collect_day_places(keywords, center_lat, center_lng, anchors, transport, warnings)
            if not places:
                warnings.append(f"day{day_number} 수집 결과 0개")

            filtered = filter_day(places, avoid_activities, anchors, used_place_ids)
            used_place_ids.update(p["id"] for p in filtered)

            filtered_by_day[day_number] = filtered
            all_filtered.extend(filtered)
            warnings.append(f"day{day_number} 앵커 {len(anchors)}개 / 수집 {len(places)}개 → 필터링 후 {len(filtered)}개")

    return {
        "filtered_candidates": all_filtered,
        "filtered_by_day":     filtered_by_day,
        "user_input":          ui,
        "warnings":            warnings,
        "step":                "filtered",
    }