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
#   endpoint 케이스: 현재 목표(mid 통과 전엔 mid, 통과 후엔 end) 방향으로
#     진행하는(현재 위치보다 목표에 더 가까운) 후보만 사용
#     (역행 후보 완전 제외, 진행 방향 후보가 없을 때만 부득이하게 전체 후보 사용)
#   교차 방지: 후보를 추가했을 때 새 구간이 지금까지의 경로(직전 구간 제외)와
#     교차하는지 선택 단계에서 미리 검증해, 교차 안 나는 후보를 우선 사용
#     (교차 안 나는 후보가 전혀 없을 때만 부득이하게 전체 허용 — 사후 검증에서
#      1건까지는 통과시키므로 완전히 막히지 않음)
#   category_name 중복 사전 차단: 이미 방문한 장소와 category_name 마지막 depth가
#     같은 후보(food/cafe 제외)는 애초에 선택 대상에서 제외
#   마지막 슬롯: end 좌표에 가까운 장소 우선 선택 (endpoint 케이스)
#   점심 슬롯: 술집/고기류 제외
#   excluded_place_ids: rollback 시 제외 목록
# ─────────────────────────────────────────────────────────────────────

import random
import math
from utils.route.route_check import segments_intersect


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
    mid_lat:            float = None,
    mid_lng:            float = None,
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
    has_mid     = mid_lat is not None and mid_lng is not None
    mid_passed  = False  # mid 경유지에 충분히 가까워졌는지 여부

    # mid가 있으면 1단계 목표는 mid, 통과 후엔 end로 전환
    def current_target():
        if has_mid and not mid_passed:
            return mid_lat, mid_lng
        return end_lat, end_lng

    MID_PASS_THRESHOLD_KM = 0.8  # 이 거리 이내로 접근하면 mid를 "통과"한 것으로 간주

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
        nonlocal current_time, current_idx, total_travel, mid_passed

        current_place = visited[-1]["place"]

        # 점심 슬롯 제외 키워드 적용
        is_food_slot = allowed_buckets == ["food"]

        # 이미 방문한 장소들의 category_name 마지막 depth (food/cafe 제외) 집합
        visited_category_lasts = set()
        for v in visited:
            v_bucket = v["place"].get("bucket", "")
            if v_bucket in ("food", "cafe"):
                continue
            v_category = v["place"].get("category", "") or ""
            v_parts = [p.strip() for p in v_category.split(">")]
            v_last  = v_parts[-1] if v_parts else ""
            if v_last:
                visited_category_lasts.add(v_last)

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
            # category_name 마지막 depth 중복 사전 차단 (food/cafe 제외)
            item_bucket = item["place"].get("bucket", "")
            if item_bucket not in ("food", "cafe"):
                item_category = item["place"].get("category", "") or ""
                item_parts = [p.strip() for p in item_category.split(">")]
                item_last  = item_parts[-1] if item_parts else ""
                if item_last and item_last in visited_category_lasts:
                    return False
            return True

        # 후보를 추가했을 때 기존 경로(직전 구간 제외, 자기 자신과 인접한 구간은 교차 검사 의미 없음)와
        # 교차하는지 미리 체크. 기존 구간 좌표쌍을 캐싱해두고 새 구간(current_place→후보)과 비교.
        existing_segments = [
            ((visited[i]["place"]["lat"], visited[i]["place"]["lng"]),
             (visited[i+1]["place"]["lat"], visited[i+1]["place"]["lng"]))
            for i in range(len(visited) - 1)
        ]

        def causes_intersection(item) -> bool:
            new_p1 = (current_place["lat"], current_place["lng"])
            new_p2 = (item["place"]["lat"], item["place"]["lng"])
            # 마지막 구간(현재 위치로 이어지는 직전 구간)은 새 구간과 인접하므로 검사 제외
            for seg_p1, seg_p2 in existing_segments[:-1] if existing_segments else []:
                if segments_intersect(new_p1, new_p2, seg_p1, seg_p2):
                    return True
            return False

        selectable_all = [item for item in candidates if is_selectable(item)]
        if not selectable_all:
            return False

        if is_last and is_endpoint:
            # 마지막 슬롯: 항상 end 좌표에 가까운 순 (mid 통과 여부 무관)
            pool_sorted = sorted(selectable_all, key=lambda item: haversine(
                item["place"]["lat"], item["place"]["lng"], end_lat, end_lng
            ))
        elif is_endpoint:
            # endpoint 케이스: 현재 목표(mid 또는 end) 방향으로 진행하는 후보만 사용
            target_lat, target_lng = current_target()
            dist_to_target_from_current = haversine(
                current_place["lat"], current_place["lng"], target_lat, target_lng
            )
            forward = [
                item for item in selectable_all
                if haversine(item["place"]["lat"], item["place"]["lng"], target_lat, target_lng)
                   < dist_to_target_from_current
            ]
            pool = forward if forward else selectable_all

            # 교차 사전 필터: 추가 시 기존 경로와 교차하지 않는 후보를 우선 사용
            non_crossing = [item for item in pool if not causes_intersection(item)]
            if non_crossing:
                pool = non_crossing

            pool_sorted = sorted(pool, key=lambda item:
                time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]])
        else:
            pool_sorted = sorted(selectable_all, key=lambda item:
                time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]])

        # 방향성 정렬된 순서를 유지한 채, travel_limit 이내 후보를 우선 사용
        # (이내 후보가 없으면 부득이하게 전체 후보로 fallback)
        within_limit = [
            item for item in pool_sorted
            if time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= travel_limit
        ]
        if within_limit:
            pool_sorted = within_limit

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

        # mid 통과 여부 갱신: 새로 방문한 장소가 mid에 충분히 가까우면 통과 처리
        if has_mid and not mid_passed:
            dist_to_mid = haversine(
                best_item["place"]["lat"], best_item["place"]["lng"], mid_lat, mid_lng
            )
            if dist_to_mid <= MID_PASS_THRESHOLD_KM:
                mid_passed = True
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