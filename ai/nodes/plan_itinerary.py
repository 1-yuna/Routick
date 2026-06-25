# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# Greedy NN으로 day별 N개 동선 생성 + 조건에 따라 동선 제외
#
# 흐름:
#   1. day별 독립 동선 생성
#      - only 케이스: 이전 day 선택 장소 제외하며 순차 생성
#      - endpoint 케이스: start/end 좌표 기반 동선 생성
#   2. 조건에 따라 동선 제외
#      - 경로 교차 (X자 동선) 제외
#      - 이동시간 초과 제외
#      - 동선 내 동일 place_tags 2개 이상 제외
#      - 점심(13:00 이전) 고기/바/술집 제외
#   3. 중복 동선 제거 (유사도 70% 이상)
#   4. 점수 기반 day별 상위 5개 반환
#   5. 후보 부족 시 fallback (조건 완화 후 재시도)
# ─────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from utils.route.greedy_nn import greedy_nn, STAY_MINUTES, haversine
from utils.route.route_check import check_route_intersections


# ─── 이동시간 초과 기준 (분) ───
TRAVEL_TIME_LIMIT = {
    "도보":   20,
    "자동차": 30,
}

# ─── 시작점당 반복 횟수 ───
REPEAT_PER_START = 3

# ─── day별 최대 동선 수 ───
MAX_ITINERARIES_PER_DAY = 5

# ─── fallback 시 완화 기준 ───
FALLBACK_TRAVEL_LIMIT_ADD  = 10  # 이동시간 초과 기준 +10분
FALLBACK_TAGS_ALLOW        = 2   # place_tags 중복 허용 개수 상향


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
        bucket = place.get("bucket", "other")
        stay   = STAY_MINUTES.get(bucket, 90)

        if order == 0:
            travel_min = 0
        else:
            prev_pid   = route[order - 1]["place"]["id"]
            prev_idx   = id_to_idx.get(prev_pid, 0)
            curr_idx   = id_to_idx.get(pid, 0)
            travel_min = time_matrix[prev_idx][curr_idx]

        arrive_dt = current_time + timedelta(minutes=travel_min)
        leave_dt  = arrive_dt + timedelta(minutes=stay)

        if order < len(route) - 1:
            next_pid        = route[order + 1]["place"]["id"]
            next_idx        = id_to_idx.get(next_pid, 0)
            curr_idx        = id_to_idx.get(pid, 0)
            travel_to_next  = int(time_matrix[curr_idx][next_idx])
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


# ─── 동선 유사도 계산 ───
def similarity(itin1: list[dict], itin2: list[dict]) -> float:
    ids1 = set(item["place"]["id"] for item in itin1)
    ids2 = set(item["place"]["id"] for item in itin2)
    intersection = ids1 & ids2
    union        = ids1 | ids2
    return len(intersection) / len(union) if union else 0


# ─── 동선 유효성 검증 ───
def is_valid_route(
    itinerary:    list[dict],
    travel_limit: int,
    max_same_tags: int = 1,
) -> tuple[bool, str]:

    # 이동시간 초과
    if any(item["travel_to_next_minutes"] > travel_limit for item in itinerary[:-1]):
        return False, "이동시간 초과"

    # place_tags 중복
    place_tags_list = []
    for item in itinerary:
        tags = item["place"].get("place_tags", [])
        for tag in tags:
            if tag in ("카페",):
                continue
            if place_tags_list.count(tag) >= max_same_tags:
                return False, f"place_tags 중복: {tag}"
            place_tags_list.append(tag)

    # 점심 슬롯 고기/바/술집
    for item in itinerary:
        if item["arrive_at"] < "13:00":
            tags = item["place"].get("place_tags", [])
            if any(tag in ("고기", "바/술집") for tag in tags):
                return False, "점심 슬롯 부적합 place_tags"

    # 경로 교차
    if check_route_intersections(itinerary):
        return False, "경로 교차"

    return True, ""


# ─── 단일 day 동선 생성 ───
def _generate_day_routes(
    candidates:         list[dict],
    place_index:        list[str],
    time_matrix:        list[list[float]],
    total_minutes:      int,
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
                total_minutes=total_minutes,
                travel_limit=travel_limit,
                excluded_place_ids=excluded_place_ids,
                end_lat=end_lat,
                end_lng=end_lng,
            )
            if not route:
                continue

            itinerary = assign_times(route, start_time, time_matrix, place_index)
            all_routes.append({
                "itinerary":   itinerary,
                "total_travel": total_travel,
                "total_score":  sum(item["place"].get("total_score", 0) for item in route),
            })

    return all_routes


# ─── [노드] N개 동선 생성 ───
def plan_itinerary(state: dict) -> dict:
    ui               = state["user_input"]
    shortlist_by_day = state.get("shortlist_by_day", {})
    time_matrix_by_day  = state.get("time_matrix_by_day", {})
    place_index_by_day  = state.get("place_index_by_day", {})
    excluded_place_ids  = set(state.get("excluded_place_ids", []))

    route_type   = ui.get("route_type", "only")
    transport_kr = ui.get("transport_kr", "도보")
    start_time   = ui.get("start_time", "09:00")
    end_time     = ui.get("end_time", "22:00")
    travel_days  = ui.get("travel_days", 1)
    days_raw     = ui.get("days") or []

    warnings: list[str] = []

    total_minutes = int((to_dt(end_time) - to_dt(start_time)).total_seconds() / 60)
    travel_limit  = TRAVEL_TIME_LIMIT.get(transport_kr, 20)

    itineraries_by_day: dict[int, list[list[dict]]] = {}

    # only 케이스: 이전 day 선택 장소 누적 제외
    used_place_ids: set[str] = set(excluded_place_ids)

    for day_number in sorted(shortlist_by_day.keys()):
        shortlist   = shortlist_by_day[day_number]
        time_matrix = time_matrix_by_day.get(day_number, [])
        place_index = place_index_by_day.get(day_number, [])

        if not shortlist or not time_matrix:
            warnings.append(f"day{day_number} shortlist/matrix 없음 → 스킵")
            continue

        # endpoint 케이스: day별 end 좌표 추출
        end_lat = end_lng = None
        start_lat = start_lng = None
        if route_type == "endpoint":
            day_raw = next((d for d in days_raw if d["day_number"] == day_number), None)
            if day_raw:
                end_lat   = day_raw.get("end_lat")
                end_lng   = day_raw.get("end_lng")
                start_lat = day_raw.get("start_lat")
                start_lng = day_raw.get("start_lng")

        # shortlist에서 ScoredPlace → candidates 형식으로 변환
        candidates = [
            {**s, "place": {**s["place"], "total_score": s["total_score"]}}
            for s in shortlist
            if s["place"]["id"] not in used_place_ids
        ]

        if not candidates:
            warnings.append(f"day{day_number} 후보 없음 (전부 제외됨)")
            continue

        # 동선 생성
        all_routes = _generate_day_routes(
            candidates=candidates,
            place_index=place_index,
            time_matrix=time_matrix,
            total_minutes=total_minutes,
            travel_limit=travel_limit,
            start_time=start_time,
            excluded_place_ids=used_place_ids,
            end_lat=end_lat,
            end_lng=end_lng,
        )

        # 유효성 검증
        valid_routes = []
        for r in all_routes:
            ok, reason = is_valid_route(r["itinerary"], travel_limit)
            if ok:
                valid_routes.append(r)

        # fallback: 유효 동선 3개 미만이면 조건 완화 후 재시도
        if len(valid_routes) < 3:
            warnings.append(f"day{day_number} 유효 동선 {len(valid_routes)}개 → fallback 시도")
            fallback_routes = _generate_day_routes(
                candidates=candidates,
                place_index=place_index,
                time_matrix=time_matrix,
                total_minutes=total_minutes,
                travel_limit=travel_limit + FALLBACK_TRAVEL_LIMIT_ADD,
                start_time=start_time,
                excluded_place_ids=used_place_ids,
                end_lat=end_lat,
                end_lng=end_lng,
            )
            for r in fallback_routes:
                ok, _ = is_valid_route(r["itinerary"], travel_limit + FALLBACK_TRAVEL_LIMIT_ADD, max_same_tags=FALLBACK_TAGS_ALLOW)
                if ok:
                    valid_routes.append(r)

        if not valid_routes:
            warnings.append(f"day{day_number} fallback도 실패 → 전체 동선 사용")
            valid_routes = all_routes

        # 중복 동선 제거 (유사도 70% 이상)
        diverse_routes = []
        for route in sorted(valid_routes, key=lambda x: x["total_score"], reverse=True):
            is_dup = any(similarity(route["itinerary"], s["itinerary"]) >= 0.7 for s in diverse_routes)
            if not is_dup:
                diverse_routes.append(route)

        # 상위 5개
        top_routes = diverse_routes[:MAX_ITINERARIES_PER_DAY]
        itineraries_by_day[day_number] = [r["itinerary"] for r in top_routes]

        warnings.append(f"day{day_number} 동선 후보: {len(top_routes)}개")

        # only/endpoint 모두: 모든 후보 동선에 등장한 장소 전부 다음 day에서 제외
        if top_routes:
            for route in top_routes:
                for item in route["itinerary"]:
                    used_place_ids.add(item["place"]["id"])

    return {
        "itineraries_by_day": itineraries_by_day,
        "warnings":           warnings,
        "step":               "itinerary_planned",
    }