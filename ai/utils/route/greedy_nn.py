# ─────────────────────────────────────────────────────────────────────
# greedy_nn
# ─────────────────────────────────────────────────────────────────────
# Greedy Nearest Neighbor 알고리즘
#
# 흐름:
#   슬롯 기반 동선 생성
#   슬롯 1: activity 또는 cafe
#   슬롯 2: food (점심)
#   슬롯 3: cafe
#   슬롯 4: activity
#   슬롯 5: activity
#   슬롯 6: food (저녁)
#   슬롯 7: lodging (plan_itinerary에서 추가)
# ─────────────────────────────────────────────────────────────────────

import random


# ─── bucket별 체류시간 (분) ───
STAY_MINUTES = {
    "cafe":     90,
    "food":     90,
    "activity": 120,
    "other":    90,
    "lodging":  0,
}

# ─── 슬롯 정의 ───
SLOTS = [
    {"bucket": ["activity", "cafe", "other"],  "label": "슬롯1"},
    {"bucket": ["food"],                        "label": "점심"},
    {"bucket": ["cafe"],                        "label": "카페"},
    {"bucket": ["activity", "other"],           "label": "슬롯4"},
    {"bucket": ["activity", "other"],           "label": "슬롯5"},
    {"bucket": ["food"],                        "label": "저녁"},
]


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

    visited = []
    visited_ids = set()
    visited_names = set()
    total_travel = 0.0
    used_minutes = 0.0

    # 시작 장소는 슬롯1 bucket만 허용
    first = candidates[start_idx]
    if first["place"].get("bucket") not in SLOTS[0]["bucket"]:
        return [], float("inf")

    visited.append(first)
    visited_ids.add(first["place"]["id"])
    visited_names.add(first["place"].get("name", ""))
    used_minutes += STAY_MINUTES.get(first["place"].get("bucket", "other"), 60)
    current_idx = id_to_matrix_idx[first["place"]["id"]]

    # 슬롯 2~6 순서대로 채우기
    for slot in SLOTS[1:]:
        allowed_buckets = slot["bucket"]

        # travel_limit 이내 + 허용 bucket + 미방문 장소
        selectable = [
            item for item in candidates
            if item["place"]["id"] not in visited_ids
            and item["place"].get("name", "") not in visited_names
            and item["place"].get("bucket") in allowed_buckets
            and time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= travel_limit
        ]

        if not selectable:
            # travel_limit 이내 없으면 전체에서 찾기
            selectable = [
                item for item in candidates
                if item["place"]["id"] not in visited_ids
                and item["place"].get("name", "") not in visited_names
                and item["place"].get("bucket") in allowed_buckets
            ]

        if not selectable:
            continue

        # 가까운 순 5개 중 랜덤 선택
        pool_sorted = sorted(
            selectable,
            key=lambda item: time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]]
        )
        top5 = pool_sorted[:5]
        best_item = random.choice(top5)

        travel_time = time_matrix[current_idx][id_to_matrix_idx[best_item["place"]["id"]]]
        next_bucket = best_item["place"].get("bucket", "other")
        next_stay = STAY_MINUTES.get(next_bucket, 60)

        # 총 여행시간 초과 시 스킵
        if used_minutes + travel_time + next_stay > total_minutes:
            continue

        visited.append(best_item)
        visited_ids.add(best_item["place"]["id"])
        visited_names.add(best_item["place"].get("name", ""))
        total_travel += travel_time
        used_minutes += travel_time + next_stay
        current_idx = id_to_matrix_idx[best_item["place"]["id"]]

    return visited, total_travel