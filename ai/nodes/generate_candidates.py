# ─────────────────────────────────────────────────────────────────────
# generate_candidates
# ─────────────────────────────────────────────────────────────────────
# 버킷 분류 + 이동시간 행렬 계산 + Greedy NN으로 모든 동선 후보 생성
#
# 흐름:
#   1. 버킷 분류 (category_group_code + category_name + name 기반)
#   2. 이동시간 행렬 계산 (day별 독립)
#   3. Greedy NN 실행 (day별, 시작점당 3회 반복)
#      - 슬롯 기반 동선 생성 (시간 조건 포함)
#      - rollback 시 excluded_place_ids 제외
#   4. 조건에 따라 동선 제외
#      - 경로 교차 (X자 동선) 제외
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
) -> tuple[bool, str]:

    # 이동시간 초과
    if any(item["travel_to_next_minutes"] > travel_limit for item in itinerary[:-1]):
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

    # 경로 교차
    if check_route_intersections(itinerary):
        return False, "경로 교차"

    return True, ""


# ─── 단일 day 동선 생성 ───
def _generate_day_routes(
    candidates:         list[dict],
    place_index:        list[str],
    time_matrix:        list[list[float]],
    travel_limit:       int,
    start_time:         str,
    excluded_place_ids: set[str],
    end_lat:            float = None,
    end_lng:            float = None,
) -> list[dict]:
    all_routes = []

    for i in range(len(candidates)):
        for _ in range(REPEAT_PER_START):
            route, total_travel = greedy_nn(
                start_idx=i,
                candidates=candidates,
                place_index=place_index,
                time_matrix=time_matrix,
                total_minutes=0,  # greedy_nn에서 시간 기반으로 처리
                travel_limit=travel_limit,
                excluded_place_ids=excluded_place_ids,
                end_lat=end_lat,
                end_lng=end_lng,
                start_time=start_time,
            )
            if not route:
                continue

            itinerary = assign_times(route, start_time, time_matrix, place_index)
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

        # endpoint 케이스: day별 end 좌표 추출
        end_lat = end_lng = None
        if route_type == "endpoint":
            day_raw = next((d for d in days_raw if d["day_number"] == day_number), None)
            if day_raw:
                end_lat = day_raw.get("end_lat")
                end_lng = day_raw.get("end_lng")

        # 3. Greedy NN 동선 생성
        all_routes = _generate_day_routes(
            candidates=candidates,
            place_index=place_index,
            time_matrix=time_matrix,
            travel_limit=travel_limit,
            start_time=start_time,
            excluded_place_ids=used_place_ids,
            end_lat=end_lat,
            end_lng=end_lng,
        )

        # 4. 유효성 검증
        valid_routes = []
        invalid_routes = []
        for r in all_routes:
            ok, reason = is_valid_route(r["itinerary"], travel_limit)
            if ok:
                valid_routes.append(r)
            else:
                invalid_routes.append({**r, "invalid_reason": reason})

        all_routes_by_day[day_number]     = all_routes
        valid_routes_by_day[day_number]   = valid_routes
        invalid_routes_by_day[day_number] = invalid_routes

        warnings.append(f"day{day_number} 전체 동선: {len(all_routes)}개, 유효: {len(valid_routes)}개, 제외: {len(invalid_routes)}개")

        # used_place_ids 갱신 (only 케이스)
        if route_type == "only" and valid_routes:
            for route in valid_routes:
                for item in route["itinerary"]:
                    used_place_ids.add(item["place"]["id"])

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