# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# Greedy NN으로 N개 동선 생성 + 조건에 따라 동선 제외
#
# 흐름:
#   1. 모든 시작점 기준으로 Greedy NN 실행 (시작점당 3회 반복) → N개 동선 생성
#   2. 조건에 따라 동선 제외
#      - food 2회 이상 연속 제외
#      - 나머지 bucket 3회 이상 연속 제외
#      - 경로 교차 (X자 동선) 제외
#      - 이동시간 초과 제외
#   3. 중복 동선 제거 (유사도 70% 이상)
#   4. 상위 20개 반환
# ─────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from utils.route.greedy_nn import greedy_nn, STAY_MINUTES
from utils.route.route_check import check_route_intersections


# ─── 이동시간 초과 기준 (분) ───
TRAVEL_TIME_LIMIT = {
    "도보":   20,
    "자동차": 30,
}

# ─── 시작점당 반복 횟수 ───
REPEAT_PER_START = 3


# ─── 시간 문자열 → datetime ───
def to_dt(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M")


# ─── datetime → 시간 문자열 ───
def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── 동선 시간 배치 ───
def assign_times(route: list[dict], start_time: str, time_matrix: list[list[float]], place_index: list[str]) -> list[dict]:
    id_to_idx = {pid: i for i, pid in enumerate(place_index)}
    itinerary = []
    current_time = to_dt(start_time)

    for order, item in enumerate(route):
        place = item["place"]
        pid = place["id"]
        bucket = place.get("bucket", "other")
        stay = STAY_MINUTES.get(bucket, 60)

        if order == 0:
            travel_min = 0
        else:
            prev_pid = route[order - 1]["place"]["id"]
            prev_idx = id_to_idx.get(prev_pid, 0)
            curr_idx = id_to_idx.get(pid, 0)
            travel_min = time_matrix[prev_idx][curr_idx]

        arrive_dt = current_time + timedelta(minutes=travel_min)
        leave_dt = arrive_dt + timedelta(minutes=stay)

        if order < len(route) - 1:
            next_pid = route[order + 1]["place"]["id"]
            next_idx = id_to_idx.get(next_pid, 0)
            curr_idx = id_to_idx.get(pid, 0)
            travel_to_next = int(time_matrix[curr_idx][next_idx])
        else:
            travel_to_next = 0

        itinerary.append({
            "order": order + 1,
            "place": place,
            "arrive_at": to_str(arrive_dt),
            "leave_at": to_str(leave_dt) if bucket != "lodging" else "-",
            "travel_to_next_minutes": travel_to_next,
            "recommendation_reason": "",
        })

        current_time = leave_dt

    return itinerary


# ─── 동선 유사도 계산 ───
def similarity(itin1: list[dict], itin2: list[dict]) -> float:
    ids1 = set(item["place"]["id"] for item in itin1)
    ids2 = set(item["place"]["id"] for item in itin2)
    intersection = ids1 & ids2
    union = ids1 | ids2
    return len(intersection) / len(union) if union else 0


# ─── [노드] N개 동선 생성 ───
def plan_itinerary(state: dict) -> dict:
    shortlist = state["shortlist"]
    time_matrix = state["time_matrix"]
    place_index = state["place_index"]
    travel_days = state["user_input"].get("travel_days", 1)
    transport_kr = state["user_input"].get("transport_kr", "도보")
    start_time = state["user_input"].get("start_time", "09:00")
    end_time = state["user_input"].get("end_time", "22:00")

    warnings = []

    # 총 여행시간 계산
    start_dt = to_dt(start_time)
    end_dt = to_dt(end_time)
    total_minutes = int((end_dt - start_dt).total_seconds() / 60)

    # lodging 분리
    lodging_items = [i for i in shortlist if i["place"].get("bucket") == "lodging"]
    lodging_items.sort(key=lambda x: x["total_score"], reverse=True)

    if travel_days > 1 and not lodging_items:
        warnings.append("lodging 후보 없음 → 숙박 슬롯 스킵")

    # lodging 제외 candidates
    candidates = [
        i for i in shortlist
        if i["place"].get("bucket") != "lodging"
    ]

    travel_limit = TRAVEL_TIME_LIMIT.get(transport_kr, 20)

    # ─── 1. 모든 시작점 기준으로 Greedy NN 실행 (시작점당 3회 반복) ───
    all_routes = []
    for i in range(len(candidates)):
        for _ in range(REPEAT_PER_START):
            route, total_travel = greedy_nn(
                i, candidates, place_index, time_matrix, total_minutes, travel_limit
            )
            if not route:
                continue

            lodging_item = lodging_items[i % len(lodging_items)] if lodging_items else None

            final_route = list(route)
            if lodging_item:
                final_route.append(lodging_item)

            itinerary = assign_times(final_route, start_time, time_matrix, place_index)
            all_routes.append({
                "itinerary": itinerary,
                "total_travel": total_travel,
                "total_score": sum(item["place"].get("total_score", 0) for item in final_route),
            })

    print(f"전체 동선: {len(all_routes)}개")

    # ─── 2. 조건에 따라 동선 제외 ───
    excluded_travel = 0
    excluded_bucket = 0
    excluded_cross  = 0
    valid_routes = []

    for r in all_routes:
        itinerary = r["itinerary"]

        # 이동시간 초과 체크
        if any(item["travel_to_next_minutes"] > travel_limit for item in itinerary):
            excluded_travel += 1
            continue

        # bucket 연속 체크
        buckets = [item["place"].get("bucket", "other") for item in itinerary]
        bucket_fail = False
        for i in range(len(buckets) - 1):
            if buckets[i] == "food" and buckets[i + 1] == "food":
                bucket_fail = True
                break
            if buckets[i] != "food" and i >= 2:
                if buckets[i] == buckets[i - 1] == buckets[i - 2]:
                    bucket_fail = True
                    break
        if bucket_fail:
            excluded_bucket += 1
            continue

        # 경로 교차 체크
        if check_route_intersections(itinerary):
            excluded_cross += 1
            continue

        valid_routes.append(r)

    print(f"이동시간 초과 제거: {excluded_travel}개")
    print(f"bucket 연속 제거: {excluded_bucket}개")
    print(f"경로 교차 제거: {excluded_cross}개")
    print(f"조건 통과: {len(valid_routes)}개")

    if not valid_routes:
        warnings.append("조건 통과한 동선 없음 → 전체 동선 사용")
        valid_routes = all_routes

    # ─── 3. 중복 동선 제거 (유사도 70% 이상이면 제거) ───
    diverse_routes = []
    for route in valid_routes:
        is_duplicate = False
        for selected in diverse_routes:
            if similarity(route["itinerary"], selected["itinerary"]) >= 0.7:
                is_duplicate = True
                break
        if not is_duplicate:
            diverse_routes.append(route)

    print(f"중복 제거 후: {len(diverse_routes)}개")

    # ─── 4. 상위 20개 반환 ───
    itineraries = [r["itinerary"] for r in diverse_routes[:20]]

    if not itineraries:
        warnings.append("itineraries 비어있음")

    return {
        "itineraries": itineraries,
        "warnings": warnings,
        "step": "itinerary_planned",
    }