# ─────────────────────────────────────────────────────────────────────
# preprocess_input
# ─────────────────────────────────────────────────────────────────────
# 전처리 노드
#
# 흐름:
#   1. 변수값 매핑 (영어 → 한국어)
#   2. travel_date → 요일 변환 (영업시간 체크용)
#   3. 키워드 설정 (맛집/카페 기본 포함)
#   4. route_type에 따라 day별 검색 파라미터 계산
#      - 케이스 1 (only): 원형 반경 (center_lat/lng + radius_km)
#      - 케이스 2 (endpoint): 사각형 영역 (rect_min/max_lat/lng)
# ─────────────────────────────────────────────────────────────────────

import math
from datetime import datetime

from constants.mapping import (
    TRAVEL_DAYS_MAP,
    COMPANION_MAP,
    TRANSPORT_MAP,
    MOODS_MAP,
    ACTIVITIES_MAP,
    WEEKDAY_MAP,
    RADIUS_MAP,
    MARGIN_MAP,
)


# ─── km → 위도 변환 (1도 ≈ 111km) ───
def km_to_lat(km: float) -> float:
    return km / 111.0


# ─── km → 경도 변환 (위도에 따라 달라짐) ───
def km_to_lng(km: float, lat: float) -> float:
    return km / (111.0 * math.cos(math.radians(lat)))


# ─── [노드] 전처리 ───
def preprocess_input(state: dict) -> dict:
    ui = dict(state["user_input"])
    warnings = []

    # ── 1. 변수값 매핑 ──────────────────────────────────────────────
    travel_days = ui.get("travel_days", 1)
    companion   = ui.get("companion", "")
    transport   = ui.get("transport", "walk")
    moods       = ui.get("moods") or []
    activities  = ui.get("activities") or []

    ui["companion_kr"]   = COMPANION_MAP.get(companion, companion)
    ui["transport_kr"]   = TRANSPORT_MAP.get(transport, transport)
    ui["duration_kr"]    = TRAVEL_DAYS_MAP.get(travel_days, "당일")
    ui["moods_kr"]       = [MOODS_MAP.get(m, m) for m in moods]
    ui["activities_kr"]  = [ACTIVITIES_MAP.get(a, a) for a in activities]

    # ── 2. travel_date → 요일 변환 ──────────────────────────────────
    travel_date = ui.get("travel_date", "")
    if travel_date:
        try:
            dt = datetime.strptime(travel_date, "%Y-%m-%d")
            ui["travel_weekday"] = WEEKDAY_MAP[dt.weekday()]
        except ValueError:
            warnings.append(f"travel_date 파싱 실패: {travel_date}")
            ui["travel_weekday"] = None
    else:
        warnings.append("travel_date 없음 → travel_weekday None")
        ui["travel_weekday"] = None

    # ── 3. 키워드 설정 ───────────────────────────────────────────────
    final_keywords = list(ui.get("activities_kr") or [])

    if "맛집" not in final_keywords:
        final_keywords.insert(0, "맛집")
    if "카페" not in final_keywords:
        final_keywords.insert(1, "카페")

    ui["final_keywords"] = final_keywords

    # ── 4. route_type에 따라 day별 검색 파라미터 계산 ───────────────
    route_type = ui.get("route_type", "only")

    radius_by_transport = RADIUS_MAP.get(transport, RADIUS_MAP["walk"])
    margin_by_transport = MARGIN_MAP.get(transport, MARGIN_MAP["walk"])

    radius_km = radius_by_transport.get(travel_days, 2.0)
    margin_km = margin_by_transport.get(travel_days, 0.5)

    days_info = []

    # 케이스 1: 목적지 좌표 기준 원형 반경
    if route_type == "only":
        lat = ui.get("lat")
        lng = ui.get("lng")

        if lat is None or lng is None:
            warnings.append("route_type=only인데 lat/lng 없음")

        # only 케이스는 travelDays만큼 같은 좌표로 day 생성
        for day_number in range(1, travel_days + 1):
            days_info.append({
                "day_number":   day_number,
                "center_lat":   lat,
                "center_lng":   lng,
                "radius_km":    radius_km,
                "rect_min_lat": None,
                "rect_min_lng": None,
                "rect_max_lat": None,
                "rect_max_lng": None,
                "region":       None,
                "start_region": None,
                "end_region":   None,
            })

    # 케이스 2: day별 시작·도착 좌표 기준 사각형 영역
    elif route_type == "endpoint":
        days_raw = ui.get("days") or []

        if not days_raw:
            warnings.append("route_type=endpoint인데 days 없음")

        for day in days_raw:
            start_lat = day.get("start_lat")
            start_lng = day.get("start_lng")
            end_lat   = day.get("end_lat")
            end_lng   = day.get("end_lng")

            if None in (start_lat, start_lng, end_lat, end_lng):
                warnings.append(f"day{day.get('day_number')} 좌표 누락")
                continue

            # A·B 위경도 min/max + 마진
            center_lat_for_margin = (start_lat + end_lat) / 2
            lat_margin = km_to_lat(margin_km)
            lng_margin = km_to_lng(margin_km, center_lat_for_margin)

            rect_min_lat = min(start_lat, end_lat) - lat_margin
            rect_max_lat = max(start_lat, end_lat) + lat_margin
            rect_min_lng = min(start_lng, end_lng) - lng_margin
            rect_max_lng = max(start_lng, end_lng) + lng_margin

            days_info.append({
                "day_number":   day.get("day_number"),
                "center_lat":   None,
                "center_lng":   None,
                "radius_km":    None,
                "rect_min_lat": round(rect_min_lat, 6),
                "rect_min_lng": round(rect_min_lng, 6),
                "rect_max_lat": round(rect_max_lat, 6),
                "rect_max_lng": round(rect_max_lng, 6),
                "region":       None,
                "start_region": None,
                "end_region":   None,
            })

    else:
        warnings.append(f"알 수 없는 route_type: {route_type}")

    ui["days_info"] = days_info

    return {
        "user_input": ui,
        "warnings":   warnings,
        "step":       "preprocessed",
    }