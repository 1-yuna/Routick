# ─────────────────────────────────────────────────────────────────────
# greedy_nn
# ─────────────────────────────────────────────────────────────────────
# Greedy Nearest Neighbor 알고리즘
#
# 흐름:
#   1. 시작점에서 가장 가까운 미방문 장소 선택 반복
#   2. 이동시간 + 체류시간 누적해서 총 여행시간 초과 전까지 뽑기
#   3. food는 누적 시간 기반으로 슬롯 결정
#      - 당일: 3시간 이상(12:00쯤) + food 0개 → 점심
#              6시간 이상(18:00쯤) + food 1개 → 저녁
#      - 숙박: TODO
# ─────────────────────────────────────────────────────────────────────


# ─── bucket별 체류시간 (분) ───
STAY_MINUTES = {
    "cafe": 60,
    "food": 60,
    "activity": 120,
    "other": 60,
    "lodging": 0,
}


# ─── Greedy NN 한 번 실행 ───
def greedy_nn(
    start_idx: int,
    candidates: list[dict],
    place_index: list[str],
    time_matrix: list[list[float]],
    total_minutes: int,
    duration: str = "당일",  # 추후 숙박 로직 추가 위해 미리 받아둠
) -> tuple[list[dict], float]:
    id_to_matrix_idx = {pid: i for i, pid in enumerate(place_index)}

    # food 슬롯 기준 시간 (당일)
    # TODO: 숙박 로직 추가
    lunch_after = 180   # 3시간 후 → 점심 (12:00쯤)
    dinner_after = 360  # 6시간 후 → 저녁 (18:00쯤)

    visited = []
    visited_ids = set()
    total_travel = 0.0
    used_minutes = 0.0

    # 시작 장소는 food 제외 → food면 스킵
    first = candidates[start_idx]
    if first["place"].get("bucket") == "food":
        return [], float("inf")

    first_bucket = first["place"].get("bucket", "other")
    visited.append(first)
    visited_ids.add(first["place"]["id"])
    used_minutes += STAY_MINUTES.get(first_bucket, 60)
    current_idx = id_to_matrix_idx[first["place"]["id"]]

    while True:
        food_count = sum(1 for item in visited if item["place"].get("bucket") == "food")

        # food 슬롯 판단 (누적 시간 기반)
        if food_count == 0 and used_minutes >= lunch_after:
            # 3시간 지났고 점심 아직 → food만 선택
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("bucket") == "food"
            ]
        elif food_count == 1 and used_minutes >= dinner_after:
            # 6시간 지났고 저녁 아직 → food만 선택
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("bucket") == "food"
            ]
        else:
            # 그 외 → food 제외하고 선택
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("bucket") != "food"
            ]

        # food 없을 때 fallback
        if not selectable:
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
            ]

        if not selectable:
            break

        # 가장 가까운 장소 선택 ( 이동시간 + total_score 같이 보기 50:50)
        best_score = float("inf")
        best_item = None

        for item in selectable:
            pid = item["place"]["id"]
            next_idx = id_to_matrix_idx[pid]
            travel_time = time_matrix[current_idx][next_idx]
            total_score = item.get("total_score", 0)

            # 정규화 후 합산
            norm_travel = travel_time / 30  # 이동시간 0~1
            norm_score = total_score / 90  # 점수 0~1

            # 낮을수록 좋음 (이동 짧고 + 점수 높고)
            combined = norm_travel * 0.5 - norm_score * 0.5

            if combined < best_score:
                best_score = combined
                best_item = item

        if best_item is None:
            break

        # 이동시간 + 체류시간 누적 → 총 여행시간 초과하면 해당 장소 스킵
        next_bucket = best_item["place"].get("bucket", "other")
        next_stay = STAY_MINUTES.get(next_bucket, 60)
        if used_minutes + travel_time + next_stay > total_minutes:
            visited_ids.add(best_item["place"]["id"])
            # 남은 후보 중 시간 안에 들어오는 게 없으면 종료
            remaining = total_minutes - used_minutes
            if all(
                    STAY_MINUTES.get(item["place"].get("bucket", "other"), 60) > remaining
                    for item in candidates
                    if item["place"]["id"] not in visited_ids
            ):
                break
            continue

        visited.append(best_item)
        visited_ids.add(best_item["place"]["id"])
        total_travel += travel_time
        used_minutes += travel_time + next_stay
        current_idx = id_to_matrix_idx[best_item["place"]["id"]]

    return visited, total_travel