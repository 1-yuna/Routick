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
#   slot_buckets 기록: 각 장소가 선택된 슬롯이 허용했던 bucket 전체를 함께 저장
#     (예: 슬롯1은 browse/cafe/pop 중 선택되므로 cafe가 뽑혀도 slot_buckets=[browse,cafe,pop])
#     3-8에서 영업시간 충돌로 대체 후보를 찾을 때, 같은 bucket만이 아니라
#     slot_buckets 전체 범위에서 탐색하기 위한 정보
#   마지막 슬롯: end 좌표에 가까운 장소 우선 선택 (endpoint 케이스)
#   점심 슬롯: 술집/고기류 제외
#   excluded_place_ids: rollback 시 제외 목록
# ─────────────────────────────────────────────────────────────────────

import random
import math
from utils.route.route_check import segments_intersect


# ─── bucket별 체류시간 (분, 기본값) ───
STAY_MINUTES = {
    "cafe":     60,
    "food":     90,
    "activity": 120,
    "browse":   60,
    "pop":      30,
    "parking":  0,
}

# ─── activity 세부 체류시간 override (분) *(v3.1)* ───
# bucket="activity" 기본 120분은 체험형(아쿠아리움/테마파크 등) 기준이라,
# 잠깐 들르는 전망대·포토스팟까지 2시간으로 잡히는 문제가 있었음.
# category/name에 키워드가 매칭되면 해당 분으로 대체 (숫자가 작은 것부터 검사)
ACTIVITY_STAY_OVERRIDE = [
    (30,  ["전망대", "포토존", "포토스팟", "동상", "조형물", "벽화", "출사"]),
    (60,  ["공원", "산책로", "골목", "거리", "등대"]),
    (90,  ["시장", "테마거리"]),
    (150, ["아쿠아리움", "테마파크", "놀이공원", "워터파크", "동물원"]),
]
# 해수욕장/해변은 override 없이 기본값(120분) 유지 — 물놀이·산책 포함 체류가 김


def get_stay_minutes(place: dict) -> int:
    """장소의 실제 체류시간(분). activity는 세부 유형에 따라 override,
    그 외 bucket은 STAY_MINUTES 기본값 사용."""
    bucket = place.get("bucket", "activity")
    if bucket != "activity":
        return STAY_MINUTES.get(bucket, 60)

    text = (place.get("category", "") or "") + (place.get("name", "") or "")
    for minutes, keywords in ACTIVITY_STAY_OVERRIDE:
        if any(kw in text for kw in keywords):
            return minutes
    return STAY_MINUTES["activity"]

# ─── 슬롯 정의 ───
# 슬롯1: browse, cafe, pop
# 슬롯2: 11:30 이후면 food / 아니면 activity,browse,pop 먼저 → food (food는 무조건)
# 슬롯3: 슬롯1에 cafe 나왔으면 cafe 제외 / 아니면 cafe 포함
# 슬롯4: activity, browse
# 슬롯5: 17:30 이후면 food / 아니면 activity,browse,pop 먼저 → food (food는 무조건)
# 슬롯6: activity, browse, pop
# 슬롯7~: 21:00 이전이면 계속 추가 (activity, cafe, browse, pop)
STOP_TIME = "21:00"  # 기본값 (도보 케이스)

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


# ─── 2-opt 재정렬 (총 이동거리 최소화) ───
# greedy 선택은 매 슬롯 "그 순간 가장 가까운 곳"만 보기 때문에, 멀리 있는 후보를
# 강제로 방문한 뒤(예: 점심 슬롯은 무조건 food) 남은 후보가 몰려있는 쪽으로 되돌아오는
# 지그재그가 생길 수 있음. 교차(X자) 사전 필터는 "선이 실제로 겹치는" 경우만 잡아내므로,
# 겹치지는 않지만 비효율적인 왕복 패턴은 별도로 총 이동시간을 줄이는 재정렬로 정리한다.
#
# 주의: food(점심/저녁) 아이템은 슬롯 로직이 "이 시간대에 방문"하도록 정해서 고른 것이므로
# 순서를 함부로 옮기면 점심/저녁 타이밍이 깨진다 (예: 점심 food가 뒤로 밀려 저녁 food와
# 붙어버림). 그래서 food 아이템의 인덱스는 고정하고, food와 food 사이 / 처음~첫 food /
# 마지막 food~끝 구간처럼 food로 나뉜 각 구간 "내부"에서만 2-opt를 적용한다.
# 첫 장소(슬롯1)도 고정, endpoint 케이스면 마지막 장소(도착지 인접 선정됨)도 고정한다.
def _two_opt(
        route:             list[dict],
        time_matrix:       list[list[float]],
        id_to_matrix_idx:  dict[str, int],
        fix_last:          bool = False,
) -> list[dict]:
    n = len(route)
    if n < 4:
        return route

    def travel(a, b):
        return time_matrix[id_to_matrix_idx[a["id"]]][id_to_matrix_idx[b["id"]]]

    # 고정 지점(움직이면 안 되는 인덱스): 첫 장소, food 전부, (endpoint면) 마지막 장소
    anchors = {0}
    if fix_last:
        anchors.add(n - 1)
    for idx, item in enumerate(route):
        if item["place"].get("bucket") == "food":
            anchors.add(idx)
    anchors = sorted(anchors)

    # 고정 지점 사이 구간들을 독립적으로 계산 (앵커 쌍 사이 + 마지막 앵커~배열 끝)
    runs = []
    for k in range(len(anchors) - 1):
        lo, hi = anchors[k] + 1, anchors[k + 1] - 1
        if hi - lo >= 1:
            runs.append((lo, hi))
    if anchors[-1] < n - 1:
        lo, hi = anchors[-1] + 1, n - 1
        if hi - lo >= 1:
            runs.append((lo, hi))

    route = route[:]
    for lo, hi in runs:
        improved = True
        while improved:
            improved = False
            for i in range(lo, hi):
                for j in range(i + 1, hi + 1):
                    a, b, c = route[i - 1]["place"], route[i]["place"], route[j]["place"]
                    d = route[j + 1]["place"] if j + 1 < n else None
                    old_cost = travel(a, b) + (travel(c, d) if d else 0)
                    new_cost = travel(a, c) + (travel(b, d) if d else 0)
                    if new_cost < old_cost - 0.01:
                        route[i:j + 1] = list(reversed(route[i:j + 1]))
                        improved = True
    return route


def _route_total_travel(
        route:            list[dict],
        time_matrix:      list[list[float]],
        id_to_matrix_idx: dict[str, int],
) -> float:
    return sum(
        time_matrix[id_to_matrix_idx[route[i]["place"]["id"]]][id_to_matrix_idx[route[i + 1]["place"]["id"]]]
        for i in range(len(route) - 1)
    )


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
        start_time:         str = "11:00",
        stop_time:          str = "21:00",
        taxi_limit:         int | None = None,   # *(v3)* 도보 여행: 택시 허용 하드컷(45분)
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

    visited.append({
        **first,
        "place": {**first["place"], "slot_buckets": ["browse", "cafe", "pop"]},
    })
    visited_ids.add(first_id)
    visited_names.add(first["place"].get("name", ""))
    stay = get_stay_minutes(first["place"])
    current_time += timedelta(minutes=stay)
    current_idx   = id_to_matrix_idx[first_id]

    # 슬롯1에 cafe가 나왔는지 확인
    slot1_has_cafe = first["place"].get("bucket") == "cafe"

    # ─── 저녁 food 도달 가능 여부 확인 *(v3.1)* ───
    # 저녁 전 activity 반복 루프가 힌트 앵커를 따라 해안 관광지 쪽으로 계속
    # 이동하다 보면, food가 몰려있는 클러스터(예: 시내)에서 점점 멀어져 저녁을
    # 아예 못 먹는 경우가 생김. 그걸 막기 위해 "이 위치에서 아직 갈 수 있는
    # food 후보가 있는가"를 체크하는 헬퍼.
    def _food_reachable(from_idx: int) -> bool:
        limit = taxi_limit if taxi_limit else travel_limit
        for item in candidates:
            p = item["place"]
            if p.get("bucket") != "food":
                continue
            pid = p["id"]
            if pid in visited_ids or pid in excluded_place_ids:
                continue
            if p.get("name", "") in visited_names:
                continue
            target_idx = id_to_matrix_idx.get(pid)
            if target_idx is None:
                continue
            if time_matrix[from_idx][target_idx] <= limit:
                return True
        return False

    def pick_slot(allowed_buckets: list[str], is_last: bool = False, protect_food: bool = False) -> bool:
        """슬롯 하나 채우기. 성공하면 True 반환.
        protect_food=True면, 선택 후에도 food가 여전히 도달 가능한 후보를 우선한다
        (저녁 전 activity 루프가 food 클러스터에서 멀어지는 것을 방지)."""
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
            # only 케이스(목표 좌표 없음): 방향성 필터는 적용 불가하지만,
            # 교차 사전 필터는 동일하게 적용 (지금까지의 경로와 교차 안 하는 후보 우선)
            non_crossing = [item for item in selectable_all if not causes_intersection(item)]
            pool = non_crossing if non_crossing else selectable_all

            pool_sorted = sorted(pool, key=lambda item:
            time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]])

        # 방향성 정렬된 순서를 유지한 채, travel_limit 이내 후보를 우선 사용
        # *(v3)* 이내 후보가 없으면 taxi_limit(도보 여행 45분) 이내 후보로 2차 fallback
        # (택시 태깅으로 살릴 수 있는 범위 — 그것도 없으면 부득이하게 전체 허용,
        #  45분 초과 구간은 사후 검증 is_valid_route에서 무효 처리됨)
        within_limit = [
            item for item in pool_sorted
            if time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= travel_limit
        ]
        if within_limit:
            pool_sorted = within_limit
        elif taxi_limit:
            within_taxi = [
                item for item in pool_sorted
                if time_matrix[current_idx][id_to_matrix_idx[item["place"]["id"]]] <= taxi_limit
            ]
            if within_taxi:
                pool_sorted = within_taxi

        # food 도달 가능성 보호 *(v3.1)*
        # protect_food=True(저녁 전 activity 루프)일 때, 그 후보를 찍고 나면
        # food에 더 이상 못 가게 되는 후보는 배제. 전부 배제되면(안전한 후보가
        # 하나도 없으면) 필터를 풀어 원래 풀 그대로 사용 — 빈 풀보다는 나음.
        if protect_food:
            food_safe = [
                item for item in pool_sorted
                if _food_reachable(id_to_matrix_idx[item["place"]["id"]])
            ]
            if food_safe:
                pool_sorted = food_safe

        # 힌트 앵커 우선 선택 *(v3.1)*
        # 도달 가능 범위(travel_limit/taxi_limit) 안에 힌트 앵커가 있으면
        # 일반 후보와 섞어 top5 랜덤을 돌리지 않고 앵커 후보 안에서만 선택.
        # (섞어서 고르면 앵커가 가까운 비-앵커 후보에 밀려 안 뽑히는 경우가 잦았음.
        #  예: 논골담길 방문 직후 바로 옆 도째비골스카이밸리가 있어도 안 이어지던 문제)
        anchor_candidates = [item for item in pool_sorted if item["place"].get("is_hint_anchor")]
        top5      = anchor_candidates[:5] if anchor_candidates else pool_sorted[:5]
        best_item = random.choice(top5)

        # 이 슬롯에서 허용되던 bucket 목록을 장소에 기록 (3-8 대체 탐색 범위 결정용)
        best_item = {
            **best_item,
            "place": {**best_item["place"], "slot_buckets": list(allowed_buckets)},
        }

        travel_time = time_matrix[current_idx][id_to_matrix_idx[best_item["place"]["id"]]]
        # *(v3.1)* activity 세부 체류시간 반영 — 이전엔 여기서 항상 120분으로 시간을
        # 흘려보내서, 전망대(실제 30분)를 뽑고도 내부적으론 120분 소요된 것처럼 계산돼
        # 17:30 도달 판정 등 슬롯 타이밍 전체가 틀어졌음
        next_stay   = get_stay_minutes(best_item["place"])

        if current_time + timedelta(minutes=travel_time + next_stay) > to_dt(stop_time):
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

    # ── 슬롯5: 저녁 (17:30 넘을 때까지 activity/browse/pop 반복 채움) *(v3.1)* ──
    # 기존엔 17:30 전이면 한 번만 시도하고 실패해도 바로 food로 넘어가서
    # 16시대에 저녁을 먹는 문제가 있었음. 이제 후보가 소진되거나(pick_slot 실패)
    # 17:30을 넘길 때까지 계속 채운 뒤 저녁 food로 전환.
    # protect_food=True: food 클러스터에서 점점 멀어지는 activity(예: 힌트 앵커를
    # 따라 해안 관광지 쪽으로 계속 이동)를 걸러서, 저녁을 아예 못 먹는 상황을 방지.
    # 현재 위치에서 food가 이미 도달 불가능하면(=더 가면 손해) 루프를 여기서 끊음.
    while to_str(current_time) < "17:30":
        if not _food_reachable(current_idx):
            break
        if not pick_slot(["activity", "browse", "pop"], protect_food=True):
            break
    pick_slot(["food"])  # food는 무조건

    # ── 슬롯6 ──
    pick_slot(["activity", "browse", "pop"])

    # ── 슬롯7~: stop_time 이전이면 계속 추가 ──
    # *(v3.1)* 5회 → 8회로 상한 상향. 실제로는 대부분 stop_time 도달 전에
    # 후보 소진(pick_slot 실패)으로 먼저 끝나는 경우가 많음 — shortlist 크기·
    # 카테고리 중복 차단에 따른 자연스러운 종료이며 상한 자체가 원인은 아니었음.
    MAX_EXTRA_SLOTS = 8
    extra_count = 0
    while extra_count < MAX_EXTRA_SLOTS:
        if to_str(current_time) >= stop_time:
            break
        is_last = extra_count == MAX_EXTRA_SLOTS - 1
        if not pick_slot(["activity", "cafe", "browse", "pop"], is_last=is_last):
            break
        extra_count += 1

    # ── 2-opt 재정렬: 첫 장소 고정, endpoint면 마지막 장소(도착지 인접)도 고정 ──
    visited      = _two_opt(visited, time_matrix, id_to_matrix_idx, fix_last=is_endpoint)
    total_travel = _route_total_travel(visited, time_matrix, id_to_matrix_idx)

    return visited, total_travel