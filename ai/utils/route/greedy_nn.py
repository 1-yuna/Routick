# ─────────────────────────────────────────────────────────────────────
# greedy_nn
# ─────────────────────────────────────────────────────────────────────
# Greedy Nearest Neighbor 알고리즘
#
# 흐름:
#   슬롯 기반 동선 생성 (동적 슬롯)
#   → 슬롯1: activity, browse, cafe, pop
#   → 슬롯2: food (11:30 이후면 food, 아니면 browse/pop)
#   → 슬롯3: cafe, pop
#   → 슬롯4: activity, browse
#   → 슬롯5: food (17:30 이후면 food, 아니면 activity/browse/pop)
#   → 슬롯6: activity, browse, pop
#   → 슬롯7~: 21:00 이전이면 계속 추가 (activity, browse, pop)
#   각 슬롯에서 travel_limit 이내 가까운 5개 중 랜덤 선택
#   마지막 슬롯: end 좌표에 가까운 장소 우선 선택 (endpoint 케이스)
#   점심 슬롯: 술집/고기류 제외
#   excluded_place_ids: rollback 시 제외 목록
# ─────────────────────────────────────────────────────────────────────

import random
import math


# ─── bucket별 체류시간 (분) ───
STAY_MINUTES = {
    "cafe":     60,
    "food":     90,
    "activity": 120,
    "browse":   60,
    "pop":      30,
    "parking":  0,
}

# ─── 슬롯 정의 ───
# 슬롯1: browse, cafe, pop
# 슬롯2: 11:30 이후면 food / 아니면 activity,browse,pop 먼저 → food (food는 무조건)
# 슬롯3: 슬롯1에 cafe 나왔으면 cafe 제외 / 아니면 cafe 포함
# 슬롯4: activity, browse
# 슬롯5: 17:30 이후면 food / 아니면 activity,browse,pop 먼저 → food (food는 무조건)
# 슬롯6: activity, browse, pop
# 슬롯7~: 21:00 이전이면 계속 추가 (activity, cafe, browse, pop)
STOP_TIME = "21:00"

# ─── 점심 슬롯 제외 category_name 키워드 ───
LUNCH_EXCLUDE_KEYWORDS = ["술집", "호프", "요리주점", "칵테일바", "와인바", "육류", "고기"]


# ─── Haversine (end 좌표까지 거리 계산용) ───
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ─── Greedy NN 한 번 실행 ───
def greedy_nn(
    start_idx:          int,
    candidates:         list[dict],
    place_index:        list[str],
    time_matrix:        list[list[float]],
    total_minutes:      int,
    travel_limit:       int = 20,
    excluded_place_ids: set[str] = None,
    end_lat:            float = None,
    end_lng:            float = None,
    start_time:         str = "09:00",
) -> tuple[list[dict], float]:

    if excluded_place_ids is None:
        excluded_place_ids = set()

    from datetime import datetime, timedelta

    def to_dt(t): return datetime.strptime(t, "%H:%M")
    def to_str(dt): return dt.strftime("%H:%M")

    id_to_matrix_idx = {pid: i for i, pid in enumerate(place_index)}

    visited       = []
    visited_ids   = set()
    visited_names = set()
    total_travel  = 0.0
    current_time  = to_dt(start_time)

    is_endpoint = end_lat is not None and end_lng is not None

    # 시작 장소 (슬롯1: browse, cafe, pop)
    first    = candidates[start_idx]
    first_id = first["place"]["id"]

    if first["place"].get("bucket") not in ["browse", "cafe", "pop"]:
        return [], float("inf")
    if first_id in excluded_place_ids:
        return [], float("inf")

    visited.append(first)
    visited_ids.add(first_id)
    visited_names.add(first["place"].get("name", ""))
    stay = STAY_MINUTES.get(first["place"].get("bucket", "cafe"), 60)
    current_time += timedelta(minutes=stay)
    current_idx   = id_to_matrix_idx[first_id]

    # 슬롯1에 cafe가 나왔는지 확인
    slot1_has_cafe = first["place"].get("bucket") == "cafe"

    def pick_slot(allowed_buckets: list[str], is_last: bool = False) -> bool:
        """슬롯 하나 채우기. 성공하면 True 반환."""
        nonlocal current_time, current_idx, total_travel

        # 점심 슬롯 제외 키워드 적용
        is_food_slot = allowed_buckets == ["food"]

        def is_selectable(item):
            if item["place"]["id"] in visited_ids:
                return False
            if item["place"]["id"] in excluded_place_ids:
                return False
            if item["place"].get("name", "") in visited_names:
                return False
            if item["place"].get("bucket") not in allowed_buckets:
                return False
            if is_food_slot:
                category = item["place"].get("category", "") or ""
                if any(kw in category for kw in LUNCH_EXCLUDE_KEYWORDS):
                    return False
            return True

        selectable = [
            item for item in candidates
            if is_selectable(item)
            and time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= travel_limit
        ]
        if not selectable:
            selectable = [item for item in candidates if is_selectable(item)]
        if not selectable:
            return False

        if is_last and is_endpoint:
            pool_sorted = sorted(selectable, key=lambda item: haversine(
                item["place"]["lat"], item["place"]["lng"], end_lat, end_lng
            ))
        else:
            pool_sorted = sorted(selectable, key=lambda item:
                time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]])

        top5      = pool_sorted[:5]
        best_item = random.choice(top5)

        travel_time = time_matrix[current_idx][id_to_matrix_idx[best_item["place"]["id"]]]
        next_bucket = best_item["place"].get("bucket", "activity")
        next_stay   = STAY_MINUTES.get(next_bucket, 90)

        if current_time + timedelta(minutes=travel_time + next_stay) > to_dt(STOP_TIME):
            return False

        visited.append(best_item)
        visited_ids.add(best_item["place"]["id"])
        visited_names.add(best_item["place"].get("name", ""))
        total_travel += travel_time
        current_time += timedelta(minutes=travel_time + next_stay)
        current_idx   = id_to_matrix_idx[best_item["place"]["id"]]
        return True

    # ── 슬롯2: 점심 (시간 안 맞으면 activity/browse/pop 먼저, 그 다음 food) ──
    if to_str(current_time) < "11:30":
        pick_slot(["activity", "browse", "pop"])
    pick_slot(["food"])  # food는 무조건

    # ── 슬롯3: 슬롯1에 cafe 나왔으면 제외 ──
    slot3_buckets = ["activity", "pop", "browse"] if slot1_has_cafe else ["activity", "cafe", "pop", "browse"]
    pick_slot(slot3_buckets)

    # ── 슬롯4 ──
    pick_slot(["activity", "browse"])

    # ── 슬롯5: 저녁 (시간 안 맞으면 activity/browse/pop 먼저, 그 다음 food) ──
    if to_str(current_time) < "17:30":
        pick_slot(["activity", "browse", "pop"])
    pick_slot(["food"])  # food는 무조건

    # ── 슬롯6 ──
    pick_slot(["activity", "browse", "pop"])

    # ── 슬롯7~: 21:00 이전이면 계속 추가 ──
    extra_count = 0
    while extra_count < 5:
        if to_str(current_time) >= STOP_TIME:
            break
        is_last = extra_count == 4
        if not pick_slot(["activity", "cafe", "browse", "pop"], is_last=is_last):
            break
        extra_count += 1

    return visited, total_travel