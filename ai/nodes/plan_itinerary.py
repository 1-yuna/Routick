# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# 이동시간 행렬 기반 최적 동선 + 시간 배치
#
# 흐름:
#   1. lodging 분리 (무조건 마지막 → Greedy NN 제외)
#   2. Greedy NN으로 최적 순서 결정
#      - 실제 이동시간 + 체류시간 누적해서 총 여행시간(720분) 초과 전까지 뽑기
#      - food는 Greedy NN 내부에서 1/3, 2/3 슬롯 제약으로 처리
#   3. lodging 마지막에 추가
#   4. 시간 배치 (도착/출발시간 계산)
# ─────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from utils.route.greedy_nn import greedy_nn, STAY_MINUTES
from constants.location import DEFAULT_START_TIME, DEFAULT_END_TIME


# ─── 시간 문자열 → datetime ───
def to_dt(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M")


# ─── datetime → 시간 문자열 ───
def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── [노드] 최적 동선 + 시간 배치 ───
def plan_itinerary(state: dict) -> dict:
    shortlist = state["shortlist"]
    time_matrix = state["time_matrix"]
    place_index = state["place_index"]
    duration = state["user_input"].get("duration", "당일")

    warnings = []

    # lodging 분리 (숙박이면 마지막 고정)
    lodging_item = None
    if duration != "당일":
        lodging_items = [i for i in shortlist if i["place"].get("bucket") == "lodging"]
        lodging_items.sort(key=lambda x: x["total_score"], reverse=True)
        lodging_item = lodging_items[0] if lodging_items else None
        if not lodging_item:
            warnings.append("lodging 후보 없음 → 숙박 슬롯 스킵")

    # # lodging 제외 + excluded_ids 제외 (food 포함 → Greedy NN 내부에서 슬롯 제약 처리)
    excluded_ids = state.get("excluded_ids", [])
    candidates = [
        i for i in shortlist
        if i["place"].get("bucket") != "lodging"
           and i["place"]["id"] not in excluded_ids
    ]

    # 총 여행시간 계산
    start_dt = to_dt(DEFAULT_START_TIME)
    end_dt = to_dt(DEFAULT_END_TIME)
    total_minutes = int((end_dt - start_dt).total_seconds() / 60)  # 720분

    # 추정 방문 수 (food 슬롯 기준)
    estimated_visits = total_minutes // 95  # 평균 체류 90분 + 이동 5분

    # Greedy NN — 모든 시작점 비교 → 총 이동시간 가장 짧은 루트 선택
    best_route = []
    best_total = float("inf")

    for i in range(len(candidates)):
        route, total = greedy_nn(i, candidates, place_index, time_matrix, total_minutes, duration)
        if total < best_total:
            best_total = total
            best_route = route

    # lodging 마지막에 추가
    final_route = list(best_route)
    if lodging_item:
        final_route.append(lodging_item)

    # 시간 배치
    itinerary = []
    current_time = start_dt
    id_to_matrix_idx = {pid: i for i, pid in enumerate(place_index)}

    for order, item in enumerate(final_route):
        place = item["place"]
        pid = place["id"]
        bucket = place.get("bucket", "other")
        stay = STAY_MINUTES.get(bucket, 60)

        # 이전 장소 → 현재 장소 이동시간
        if order == 0:
            travel_min = 0
        else:
            prev_pid = final_route[order - 1]["place"]["id"]
            prev_idx = id_to_matrix_idx.get(prev_pid, 0)
            curr_idx = id_to_matrix_idx.get(pid, 0)
            travel_min = time_matrix[prev_idx][curr_idx]

        arrive_dt = current_time + timedelta(minutes=travel_min)
        leave_dt = arrive_dt + timedelta(minutes=stay)

        # 현재 장소 → 다음 장소 이동시간
        if order < len(final_route) - 1:
            next_pid = final_route[order + 1]["place"]["id"]
            next_idx = id_to_matrix_idx.get(next_pid, 0)
            curr_idx = id_to_matrix_idx.get(pid, 0)
            travel_to_next = int(time_matrix[curr_idx][next_idx])
        else:
            travel_to_next = 0

        itinerary.append({
            "order": order + 1,
            "place": place,
            "arrive_at": to_str(arrive_dt),
            "leave_at": to_str(leave_dt) if bucket != "lodging" else "-",
            "travel_to_next_minutes": travel_to_next,
            "recommendation_reason": "",  # generate_response에서 채움
        })

        current_time = leave_dt

    route = [item["place"]["id"] for item in final_route]

    return {
        "itinerary": itinerary,
        "route": route,
        "warnings": warnings,
        "step": "itinerary_planned",
    }