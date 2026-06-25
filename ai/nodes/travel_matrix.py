# ─────────────────────────────────────────────────────────────────────
# travel_matrix
# ─────────────────────────────────────────────────────────────────────
# shortlist 장소 간 이동시간 행렬 계산
#
# 흐름:
#   1. shortlist_by_day 기반 day별 독립 계산
#   2. Haversine 공식으로 장소 간 직선거리 계산 → distance_matrix
#   3. 이동수단별 평균속도로 이동시간(분) 변환 → time_matrix
# ─────────────────────────────────────────────────────────────────────

import math


# ─── 이동수단별 평균속도 (km/h) ───
SPEED_KMH = {
    "도보":   4,
    "자동차": 30,
}


# ─── Haversine 공식 → 두 좌표 간 직선거리(km) ───
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ─── 거리 → 이동시간(분) 변환 ───
def distance_to_minutes(distance_km: float, transport_kr: str) -> float:
    speed = SPEED_KMH.get(transport_kr, 4)
    return (distance_km / speed) * 60


# ─── 단일 day 행렬 계산 ───
def _build_matrix(
    shortlist: list[dict],
    transport_kr: str,
) -> tuple[list[str], list[list[float]], list[list[float]]]:

    place_index      = [item["place"]["id"] for item in shortlist]
    distance_matrix: list[list[float]] = []
    time_matrix:     list[list[float]] = []

    for i, item_a in enumerate(shortlist):
        dist_row = []
        time_row = []
        a = item_a["place"]

        for j, item_b in enumerate(shortlist):
            if i == j:
                dist_row.append(0.0)
                time_row.append(0.0)
            else:
                b    = item_b["place"]
                dist = haversine(a["lat"], a["lng"], b["lat"], b["lng"])
                mins = distance_to_minutes(dist, transport_kr)
                dist_row.append(round(dist, 3))
                time_row.append(round(mins, 1))

        distance_matrix.append(dist_row)
        time_matrix.append(time_row)

    return place_index, distance_matrix, time_matrix


# ─── [노드] 이동시간 행렬 생성 ───
def travel_matrix(state: dict) -> dict:
    shortlist_by_day = state.get("shortlist_by_day", {})
    transport_kr     = state["user_input"].get("transport_kr", "도보")

    distance_matrix_by_day: dict[int, list[list[float]]] = {}
    time_matrix_by_day:     dict[int, list[list[float]]] = {}
    place_index_by_day:     dict[int, list[str]]         = {}

    for day_number, shortlist in shortlist_by_day.items():
        place_index, distance_matrix, time_matrix = _build_matrix(shortlist, transport_kr)
        place_index_by_day[day_number]     = place_index
        distance_matrix_by_day[day_number] = distance_matrix
        time_matrix_by_day[day_number]     = time_matrix

    return {
        "place_index_by_day":     place_index_by_day,
        "distance_matrix_by_day": distance_matrix_by_day,
        "time_matrix_by_day":     time_matrix_by_day,
        "step":                   "matrix_built",
    }