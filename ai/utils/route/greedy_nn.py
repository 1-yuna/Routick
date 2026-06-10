# ─────────────────────────────────────────────────────────────────────
# greedy_nn
# ─────────────────────────────────────────────────────────────────────
# Greedy Nearest Neighbor 알고리즘
#
# 흐름:
#   1. 시작점에서 travel_limit 이내 미방문 장소 랜덤 선택
#   2. 이동시간 + 체류시간 누적해서 총 여행시간 초과 전까지 뽑기
#   3. food는 누적 시간 기반으로 슬롯 결정
#      - 3시간 경과 + food 0개 → 점심 강제 배치
#      - 6시간 경과 + food 1개 → 저녁 강제 배치
# ─────────────────────────────────────────────────────────────────────

import random


# ─── bucket별 체류시간 (분) ───
STAY_MINUTES = {
    "cafe":     60,
    "food":     60,
    "activity": 120,
    "other":    60,
    "lodging":  0,
}


# ─── Greedy NN 한 번 실행 ───
def greedy_nn(
    start_idx: int,
    candidates: list[dict],
    place_index: list[str],
    time_matrix: list[list[float]],
    total_minutes: int,
    travel_limit: int = 20,
) -> tuple[list[dict], float]:
    id_to_matrix_idx = {pid: i for i, pid in enumerate(place_index)}

    # 09:00 시작 기준 (분)
    lunch_start  = 150  # 11:30 (2.5시간 후)
    lunch_end    = 240  # 13:00 (4시간 후)
    dinner_start = 540  # 18:00 (9시간 후)
    dinner_end   = 600  # 19:00 (10시간 후)

    visited = []
    visited_ids = set()
    visited_names = set()
    total_travel = 0.0
    used_minutes = 0.0
    lunch_missed = False
    dinner_missed = False
    lunch_gave_up = False   # food 포기 여부
    dinner_gave_up = False  # food 포기 여부

    # 시작 장소는 food 제외
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

        # 슬롯 지나쳤는지 체크
        if food_count == 0 and used_minutes > lunch_end:
            lunch_missed = True
        if food_count == 1 and used_minutes > dinner_end:
            dinner_missed = True

        # food 슬롯 판단
        need_food = False
        if food_count == 0 and not lunch_gave_up and (lunch_start <= used_minutes <= lunch_end or lunch_missed):
            need_food = True
        elif food_count == 1 and not dinner_gave_up and (dinner_start <= used_minutes <= dinner_end or dinner_missed):
            need_food = True

        if need_food:
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("name", "") not in visited_names
                and item["place"].get("bucket") == "food"
            ]
        else:
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("name", "") not in visited_names
                and item["place"].get("bucket") != "food"
            ]

        # food 없을 때 fallback (non-food로 진행)
        if not selectable:
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("name", "") not in visited_names
            ]
            # food를 못 찾으면 포기 플래그 설정
            if need_food:
                if food_count == 0:
                    lunch_gave_up = True
                else:
                    dinner_gave_up = True

        if not selectable:
            break

        # travel_limit 이내 장소만 필터링
        within_limit = [
            item for item in selectable
            if time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= travel_limit
        ]

        # travel_limit 이내 장소 없으면 전체에서 선택
        pool = within_limit if within_limit else selectable

        # 거리 기반 가중치 랜덤 선택 (가까울수록 선택 확률 높음)
        weights = [
            1 / (time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] + 0.1)
            for item in pool
        ]
        best_item = random.choices(pool, weights=weights, k=1)[0]
        travel_time = time_matrix[current_idx][id_to_matrix_idx[best_item["place"]["id"]]]

        # 총 여행시간 초과 시 스킵
        next_bucket = best_item["place"].get("bucket", "other")
        next_stay = STAY_MINUTES.get(next_bucket, 60)
        if used_minutes + travel_time + next_stay > total_minutes:
            # food도 visited_names에 추가 (같은 이름 재선택 방지)
            visited_names.add(best_item["place"].get("name", ""))
            if next_bucket != "food":
                visited_ids.add(best_item["place"]["id"])
            remaining = total_minutes - used_minutes
            if all(
                STAY_MINUTES.get(item["place"].get("bucket", "other"), 60) > remaining
                for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("name", "") not in visited_names
            ):
                break
            continue

        visited.append(best_item)
        visited_ids.add(best_item["place"]["id"])
        visited_names.add(best_item["place"].get("name", ""))
        total_travel += travel_time
        used_minutes += travel_time + next_stay
        current_idx = id_to_matrix_idx[best_item["place"]["id"]]

    return visited, total_travel