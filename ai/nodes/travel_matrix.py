# ─────────────────────────────────────────────────────────────────────
# travel_matrix
# ─────────────────────────────────────────────────────────────────────
# shortlist 30개 장소 간 이동시간 행렬 계산
#
# 흐름:
#   1. shortlist에서 place_id, lat, lng 추출
#   2. 모든 장소 쌍에 대해 Haversine으로 거리 계산
#   3. 이동수단 평균속도로 이동시간(분) 변환
#   4. distance_matrix, time_matrix, place_index 저장
# ─────────────────────────────────────────────────────────────────────

from core.state import TravelState
import math


# ─── 이동수단별 평균속도 (km/h) ───
SPEED_KMH = {
    "도보": 4,
    "자전거": 12,
    "자동차": 30,
}


# ─── Haversine 공식 → 두 좌표 간 직선거리(km) ───
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371  # 지구 반지름 (km)
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ─── 거리 → 이동시간(분) 변환 ───
def distance_to_minutes(distance_km: float, transport_mode: str) -> float:
    speed = SPEED_KMH.get(transport_mode, 4)  # 기본값 도보
    return (distance_km / speed) * 60


# ─── [노드] 이동시간 행렬 생성 ───
def travel_matrix(state: TravelState) -> dict:
    shortlist = state["shortlist"]
    transport_mode = state["user_input"].get("transport_mode", "도보")

    # place_id 순서 인덱스 생성
    place_index = [item["place"]["id"] for item in shortlist]
    n = len(place_index)

    distance_matrix: list[list[float]] = []
    time_matrix: list[list[float]] = []

    for i, item_a in enumerate(shortlist):
        dist_row = []
        time_row = []
        a = item_a["place"]

        for j, item_b in enumerate(shortlist):
            if i == j:
                dist_row.append(0.0)
                time_row.append(0.0)
            else:
                b = item_b["place"]
                dist = haversine(a["lat"], a["lng"], b["lat"], b["lng"])
                mins = distance_to_minutes(dist, transport_mode)
                dist_row.append(round(dist, 3))
                time_row.append(round(mins, 1))

        distance_matrix.append(dist_row)
        time_matrix.append(time_row)

    return {
        "place_index": place_index,
        "distance_matrix": distance_matrix,
        "time_matrix": time_matrix,
        "step": "matrix_built",
    }