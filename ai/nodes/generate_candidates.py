# ─────────────────────────────────────────────────────────────────────
# generate_candidates
# ─────────────────────────────────────────────────────────────────────
# 버킷 분류 + 이동시간 행렬 계산 + Greedy NN으로 모든 동선 후보 생성
#
# 흐름:
#   1. 버킷 분류 (category_group_code + category_name + name 기반)
#   2. 이동시간 행렬 계산 (day별 독립)
#   3. Greedy NN 실행 (day별, 시작점당 5회 반복)
#      - 슬롯 기반 동선 생성 (시간 조건 포함)
#      - rollback 시 excluded_place_ids 제외
#   4. 조건에 따라 동선 제외
#      - 경로 교차 (X자 동선) 제외
#        단, 출발-도착 거리가 짧으면(SHORT_DISTANCE_THRESHOLD_KM 이하)
#        작은 원형 동선이 자연스러우므로 일정 건수(MAX_INTERSECTIONS_SHORT_DISTANCE) 허용
#      - 이동시간 초과 제외
#      - 동선 내 동일 category_name (맨 마지막 depth 기준) 2개 이상 제외 (food/cafe 제외)
#      - 점심 슬롯 술집/고기류 제외
# ─────────────────────────────────────────────────────────────────────

import math
from datetime import datetime, timedelta
from utils.route.greedy_nn import greedy_nn, STAY_MINUTES, LUNCH_EXCLUDE_KEYWORDS
from utils.route.route_check import check_route_intersections


# ─── 이동시간 초과 기준 (분) ───
TRAVEL_TIME_LIMIT = {
    "도보":   20,
    "자동차": 30,
}

# ─── 출발-도착 거리가 이 값 이하면 transport=car여도 도보 기준 적용 ───
SHORT_DISTANCE_THRESHOLD_KM = 1.0

# ─── 출발-도착 거리가 짧을 때 허용하는 경로 교차 건수 ───
MAX_INTERSECTIONS_SHORT_DISTANCE = 1

# ─── 출발=도착(거의 동일 좌표, 왕복) 기준 거리 및 교차 허용 건수 ───
# 왕복 동선은 마지막 구간이 구조적으로 이전 구간과 가까워질 수밖에 없어
# 교차 0건 달성이 어려우므로 별도로 완화된 기준 적용
ROUND_TRIP_THRESHOLD_KM   = 0.1
MAX_INTERSECTIONS_ROUND_TRIP = 1

# ─── 시작점당 반복 횟수 ───
REPEAT_PER_START = 5

# ─── 버킷 분류 키워드 ───
BUCKET_KEYWORDS = {
    "activity": [
        "박물관", "전시관", "미술관", "문화원", "전시회", "박람회", "화랑",
        "시장", "영화관", "공연장", "연극극장", "공원시설물", "아쿠아리움",
        "클라이밍", "행글라이딩", "패러글라이딩", "서바이벌게임",
        "테마파크", "해수욕장", "실내동물원", "만화카페", "보드카페",
        "방탈출카페", "오락실", "멀티방", "백화점", "도자기", "수예", "자수",
        "가죽공예", "목공예", "공원", "관광", "명소", "키즈카페", "놀이교육",
    ],
    "activity_name": [
        "짚라인", "짚트랙", "짚와이어", "아라나비", "공방", "원데이", "팝업", "플스", "파티룸",
    ],
    "browse": ["서점", "사격", "의류판매"],
    "pop":    ["사진관", "취미용품점", "기념품판매", "인테리어장식판매"],
}


# ─── 버킷 분류 ───
def classify_bucket(place: dict) -> str:
    code     = place.get("category_group_code", "") or ""
    category = place.get("category", "") or ""
    name     = place.get("name", "") or ""

    if code == "FD6":
        return "food"
    if code == "CE7":
        return "cafe"
    if "제과" in category or "베이커리" in category:
        return "cafe"
    if any(kw in category for kw in BUCKET_KEYWORDS["browse"]):
        return "browse"
    if any(kw in category for kw in BUCKET_KEYWORDS["pop"]):
        return "pop"
    if any(kw in category for kw in BUCKET_KEYWORDS["activity"]):
        return "activity"
    if any(kw in name for kw in BUCKET_KEYWORDS["activity_name"]):
        return "activity"
    return "activity"


# ─── Haversine ───
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
    speed = {"도보": 4, "자동차": 30}.get(transport_kr, 4)
    minutes = (distance_km / speed) * 60
    return max(1.0, round(minutes, 1))


# ─── 이동시간 행렬 계산 ───
def build_matrix(
    shortlist:    list[dict],
    transport_kr: str,
) -> tuple[list[str], list[list[float]], list[list[float]]]:
    place_index      = [item["place"]["id"] for item in shortlist]
    distance_matrix  = []
    time_matrix      = []

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


# ─── 시간 문자열 → datetime ───
def to_dt(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M")


# ─── datetime → 시간 문자열 ───
def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── 동선 시간 배치 ───
def assign_times(
    route:       list[dict],
    start_time:  str,
    time_matrix: list[list[float]],
    place_index: list[str],
) -> list[dict]:
    id_to_idx    = {pid: i for i, pid in enumerate(place_index)}
    itinerary    = []
    current_time = to_dt(start_time)

    for order, item in enumerate(route):
        place  = item["place"]
        pid    = place["id"]
        bucket = place.get("bucket", "activity")
        stay   = STAY_MINUTES.get(bucket, 90)

        travel_min = 0 if order == 0 else max(1, int(time_matrix[id_to_idx.get(route[order-1]["place"]["id"], 0)][id_to_idx.get(pid, 0)]))

        arrive_dt = current_time + timedelta(minutes=travel_min)
        leave_dt  = arrive_dt + timedelta(minutes=stay)

        if order < len(route) - 1:
            next_pid       = route[order + 1]["place"]["id"]
            travel_to_next = max(1, int(time_matrix[id_to_idx.get(pid, 0)][id_to_idx.get(next_pid, 0)]))
        else:
            travel_to_next = 0

        itinerary.append({
            "order":                  order + 1,
            "place":                  place,
            "arrive_at":              to_str(arrive_dt),
            "leave_at":               to_str(leave_dt),
            "travel_to_next_minutes": travel_to_next,
            "recommendation_reason":  "",
        })
        current_time = leave_dt

    return itinerary


# ─── 동선 유효성 검증 ───
def is_valid_route(
    itinerary:         list[dict],
    travel_limit:      int,
    max_same_category: int = 1,
    max_intersections: int = 0,
) -> tuple[bool, str]:

    # 이동시간 초과 (단, 출발지→첫 장소, 마지막 장소→도착지 구간은 제약 없음)
    for idx, item in enumerate(itinerary[:-1]):
        bucket = item["place"].get("bucket", "")
        if bucket == "start":
            continue  # 출발지 → 첫 장소: 이동시간 제약 없음
        # 다음 블록이 도착지(end)면, 그 직전 구간도 이동시간 제약 없음
        if itinerary[idx + 1]["place"].get("bucket") == "end":
            continue
        if item["travel_to_next_minutes"] > travel_limit:
            return False, "이동시간 초과"

    # category_name 맨 마지막 depth 기준 중복 (food/cafe 제외)
    category_last_list = []
    for item in itinerary:
        bucket = item["place"].get("bucket", "")
        if bucket in ("food", "cafe"):
            continue
        category = item["place"].get("category", "") or ""
        parts    = [p.strip() for p in category.split(">")]
        last     = parts[-1] if parts else ""
        if not last:
            continue
        if category_last_list.count(last) >= max_same_category:
            return False, f"category_name 중복: {last}"
        category_last_list.append(last)

    # 경로 교차 (출발-도착 거리가 짧으면 max_intersections만큼 허용)
    intersections = check_route_intersections(itinerary)
    if len(intersections) > max_intersections:
        return False, f"경로 교차 {len(intersections)}건"

    return True, ""


# ─── 단일 day 동선 생성 ───
def _generate_day_routes(
    candidates:         list[dict],
    place_index:        list[str],
    time_matrix:        list[list[float]],
    travel_limit:       int,
    start_time:         str,
    excluded_place_ids: set[str],
    start_lat:          float = None,
    start_lng:          float = None,
    mid_lat:            float = None,
    mid_lng:            float = None,
    end_lat:            float = None,
    end_lng:            float = None,
    start_name:         str = "출발지",
    end_name:           str = "도착지",
) -> list[dict]:
    all_routes = []
    has_start  = start_lat is not None and start_lng is not None
    has_mid    = mid_lat is not None and mid_lng is not None

    # start 좌표가 있으면 슬롯1(browse/cafe/pop) 중 1단계 목표(mid 있으면 mid, 없으면 end)
    # 방향으로 진행하는 후보만 시작점으로 사용
    if has_start:
        slot1_candidates = [
            (i, c) for i, c in enumerate(candidates)
            if c["place"].get("bucket") in ["browse", "cafe", "pop"]
        ]

        target_lat = mid_lat if has_mid else end_lat
        target_lng = mid_lng if has_mid else end_lng
        has_target = target_lat is not None and target_lng is not None

        if has_target:
            dist_to_target_from_start = haversine(start_lat, start_lng, target_lat, target_lng)

            # 목표 방향으로 진행하는(= start보다 목표에 더 가까운) 후보만 남김
            forward_candidates = [
                (i, c) for i, c in slot1_candidates
                if haversine(c["place"]["lat"], c["place"]["lng"], target_lat, target_lng) < dist_to_target_from_start
            ]
            # 역행 후보만 있으면 부득이하게 전체 후보 사용
            pool = forward_candidates if forward_candidates else slot1_candidates

            pool.sort(key=lambda x: haversine(start_lat, start_lng, x[1]["place"]["lat"], x[1]["place"]["lng"]))
        else:
            pool = sorted(
                slot1_candidates,
                key=lambda x: haversine(start_lat, start_lng, x[1]["place"]["lat"], x[1]["place"]["lng"])
            )

        start_indices = [i for i, _ in pool[:5]] or list(range(len(candidates)))
    else:
        start_indices = list(range(len(candidates)))

    for i in start_indices:
        for _ in range(REPEAT_PER_START):
            route, total_travel = greedy_nn(
                start_idx=i,
                candidates=candidates,
                place_index=place_index,
                time_matrix=time_matrix,
                total_minutes=0,  # greedy_nn에서 시간 기반으로 처리
                travel_limit=travel_limit,
                excluded_place_ids=excluded_place_ids,
                mid_lat=mid_lat,
                mid_lng=mid_lng,
                end_lat=end_lat,
                end_lng=end_lng,
                start_time=start_time,
            )
            if not route:
                continue

            itinerary = assign_times(route, start_time, time_matrix, place_index)

            # start 블록을 맨 앞에 추가
            if has_start:
                first_place = itinerary[0]["place"]
                walk_min = int(distance_to_minutes(
                    haversine(start_lat, start_lng, first_place["lat"], first_place["lng"]),
                    "도보"
                ))
                start_block = {
                    "order":                  0,
                    "place": {
                        "id":       "start",
                        "name":     start_name or "출발지",
                        "lat":      start_lat,
                        "lng":      start_lng,
                        "bucket":   "start",
                        "category": "",
                    },
                    "arrive_at":              None,
                    "leave_at":               start_time,
                    "travel_to_next_minutes": walk_min,
                    "recommendation_reason":  "",
                }
                itinerary = [start_block] + itinerary

            # end 블록을 맨 뒤에 추가
            has_end = end_lat is not None and end_lng is not None
            if has_end:
                last_place = itinerary[-1]["place"]
                walk_min_to_end = int(distance_to_minutes(
                    haversine(last_place["lat"], last_place["lng"], end_lat, end_lng),
                    "도보"
                ))
                # 마지막 장소의 travel_to_next_minutes를 end까지 이동시간으로 갱신
                itinerary[-1]["travel_to_next_minutes"] = walk_min_to_end
                end_arrive = to_str(to_dt(itinerary[-1]["leave_at"]) + timedelta(minutes=walk_min_to_end))
                end_block = {
                    "order":                  len(itinerary) + 1,
                    "place": {
                        "id":       "end",
                        "name":     end_name or "도착지",
                        "lat":      end_lat,
                        "lng":      end_lng,
                        "bucket":   "end",
                        "category": "",
                    },
                    "arrive_at":              end_arrive,
                    "leave_at":               None,
                    "travel_to_next_minutes": 0,
                    "recommendation_reason":  "",
                }
                itinerary = itinerary + [end_block]

            all_routes.append({
                "itinerary":    itinerary,
                "total_travel": total_travel,
                "total_score":  sum(item["place"].get("total_score", 0) for item in route),
            })

    return all_routes


# ─── [노드] 동선 후보 생성 ───
def generate_candidates(state: dict) -> dict:
    ui                  = state["user_input"]
    shortlist_by_day    = state.get("shortlist_by_day", {})
    excluded_place_ids  = set(state.get("excluded_place_ids", []))

    route_type   = ui.get("route_type", "only")
    transport_kr = ui.get("transport_kr", "도보")
    start_time   = ui.get("start_time", "09:00")
    days_raw     = ui.get("days") or []

    warnings: list[str] = []
    travel_limit = TRAVEL_TIME_LIMIT.get(transport_kr, 20)

    all_routes_by_day:      dict[int, list[dict]] = {}
    valid_routes_by_day:    dict[int, list[dict]] = {}
    invalid_routes_by_day:  dict[int, list[dict]] = {}
    time_matrix_by_day:     dict[int, list[list[float]]] = {}
    distance_matrix_by_day: dict[int, list[list[float]]] = {}
    place_index_by_day:     dict[int, list[str]] = {}

    used_place_ids: set[str] = set(excluded_place_ids)

    for day_number in sorted(shortlist_by_day.keys()):
        shortlist = shortlist_by_day[day_number]

        if not shortlist:
            warnings.append(f"day{day_number} shortlist 없음 → 스킵")
            continue

        # 1. 버킷 분류 + candidates 구성
        candidates = []
        for s in shortlist:
            if s["place"]["id"] in used_place_ids:
                continue
            place  = dict(s["place"])
            bucket = classify_bucket(place)
            place["bucket"] = bucket
            candidates.append({**s, "place": {**place, "total_score": s["total_score"]}})

        if not candidates:
            warnings.append(f"day{day_number} 후보 없음 (전부 제외됨)")
            continue

        # 2. 이동시간 행렬 계산
        place_index, distance_matrix, time_matrix = build_matrix(candidates, transport_kr)
        place_index_by_day[day_number]     = place_index
        distance_matrix_by_day[day_number] = distance_matrix
        time_matrix_by_day[day_number]     = time_matrix

        # endpoint 케이스: day별 start/mid/end 좌표 + 장소명 추출
        start_lat = start_lng = mid_lat = mid_lng = end_lat = end_lng = None
        start_name = end_name = None
        day_travel_limit   = travel_limit  # 기본값: 전체 transport 기준
        day_max_intersections = 0          # 기본값: 교차 허용 안 함

        if route_type == "endpoint":
            day_raw = next((d for d in days_raw if d["day_number"] == day_number), None)
            if day_raw:
                start_lat = day_raw.get("start_lat")
                start_lng = day_raw.get("start_lng")
                mid_lat   = day_raw.get("mid_lat")
                mid_lng   = day_raw.get("mid_lng")
                end_lat   = day_raw.get("end_lat")
                end_lng   = day_raw.get("end_lng")

                # 출발-도착 직선거리가 짧으면 도보 기준 적용 (작은 원형 동선은 자연스러움)
                if None not in (start_lat, start_lng, end_lat, end_lng):
                    start_end_dist = haversine(start_lat, start_lng, end_lat, end_lng)
                    if start_end_dist <= SHORT_DISTANCE_THRESHOLD_KM:
                        day_travel_limit = TRAVEL_TIME_LIMIT["도보"]

                        # 출발=도착(왕복) 케이스는 마지막 구간이 구조적으로 이전 구간과
                        # 가까워질 수밖에 없어 교차 0건 달성이 어려우므로 1건 허용
                        if start_end_dist <= ROUND_TRIP_THRESHOLD_KM:
                            day_max_intersections = MAX_INTERSECTIONS_ROUND_TRIP
                        else:
                            day_max_intersections = MAX_INTERSECTIONS_SHORT_DISTANCE

                        warnings.append(
                            f"day{day_number} 출발-도착 거리 {start_end_dist:.1f}km → "
                            f"도보 기준 + 경로 교차 {day_max_intersections}건 허용"
                        )

            days_info_list = ui.get("days_info") or []
            day_info = next((d for d in days_info_list if d.get("day_number") == day_number), None)
            if day_info:
                start_name = day_info.get("start_name")
                end_name   = day_info.get("end_name")

        # 3. Greedy NN 동선 생성
        all_routes = _generate_day_routes(
            candidates=candidates,
            place_index=place_index,
            time_matrix=time_matrix,
            travel_limit=day_travel_limit,
            start_time=start_time,
            excluded_place_ids=used_place_ids,
            start_lat=start_lat,
            start_lng=start_lng,
            mid_lat=mid_lat,
            mid_lng=mid_lng,
            end_lat=end_lat,
            end_lng=end_lng,
            start_name=start_name,
            end_name=end_name,
        )

        # 4. 유효성 검증
        valid_routes = []
        invalid_routes = []
        for r in all_routes:
            ok, reason = is_valid_route(r["itinerary"], day_travel_limit, max_intersections=day_max_intersections)
            if ok:
                valid_routes.append(r)
            else:
                invalid_routes.append({**r, "invalid_reason": reason})

        all_routes_by_day[day_number]     = all_routes
        valid_routes_by_day[day_number]   = valid_routes
        invalid_routes_by_day[day_number] = invalid_routes

        warnings.append(f"day{day_number} 전체 동선: {len(all_routes)}개, 유효: {len(valid_routes)}개, 제외: {len(invalid_routes)}개")

    return {
        "all_routes_by_day":      all_routes_by_day,
        "valid_routes_by_day":    valid_routes_by_day,
        "invalid_routes_by_day":  invalid_routes_by_day,
        "time_matrix_by_day":     time_matrix_by_day,
        "distance_matrix_by_day": distance_matrix_by_day,
        "place_index_by_day":     place_index_by_day,
        "warnings":               warnings,
        "step":                   "candidates_generated",
    }