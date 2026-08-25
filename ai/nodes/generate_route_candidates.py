# ─────────────────────────────────────────────────────────────────────
# generate_route_candidates
# ─────────────────────────────────────────────────────────────────────
# 동선 후보 생성 노드
#
# 흐름 (day별):
#   1. day별 shortlist 20개를 food/cafe/activity로 분리
#      (카페+활동 = "카페/활동" 슬롯 후보 풀)
#   2. 시작 장소를 서로 다르게 하여 최대 5개 동선 생성
#      - 슬롯 패턴: 카페/활동 → 밥 → 카페/활동 → 카페/활동 → 밥 → 카페/활동
#      - 슬롯마다 이동시간 제한 내 후보 중 점수 최고를 그리디하게 선택
#        (utils/route/route_build.py)
#      - endpoint 케이스: 마지막 슬롯만 도착지 방향으로 편향, 나머지는 mid 반경
#        shortlist 안에서 자유롭게 구성 — 실제 출발지/도착지는 앞뒤에 블록으로 붙여
#        이동시간만 계산 (출발지·도착지가 slot1/slot6과 가까울 필요는 없음)
#   3. 유효한 동선이 5개 미만이면 있는 만큼만 반환 + 경고
#
# day별로 서로 의존성이 없고 순수 계산(외부 API 호출 없음)이라 day 루프를
# 동기로 순차 처리해도 wall time에 영향 없음 — day 병렬화 불필요
# ─────────────────────────────────────────────────────────────────────

import random

from utils.route.route_build import build_route

MAX_ROUTES_PER_DAY = 5


# ─── shortlist를 bucket별 풀로 분리 ───
def _split_pools(shortlist: list[dict]) -> tuple[list[dict], list[dict]]:
    flex_pool = [p for p in shortlist if p.get("bucket") in ("cafe", "activity")]
    food_pool = [p for p in shortlist if p.get("bucket") == "food"]
    return flex_pool, food_pool


# ─── day_info에서 mid/start/end 좌표 추출 (endpoint 아니면 start/end는 None) ───
def _day_coords(day_info: dict) -> tuple:
    start_lat, start_lng = day_info.get("start_lat"), day_info.get("start_lng")
    end_lat, end_lng     = day_info.get("end_lat"), day_info.get("end_lng")
    start_coord = (start_lat, start_lng) if start_lat is not None and start_lng is not None else None
    end_coord   = (end_lat, end_lng) if end_lat is not None and end_lng is not None else None
    return start_coord, end_coord


# ─── day 하나: 최대 MAX_ROUTES_PER_DAY개의 서로 다른 시작 장소로 동선 생성 ───
def _build_day_routes(
    day_number: int,
    shortlist: list[dict],
    day_info: dict,
    transport: str,
    route_type: str,
) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    flex_pool, food_pool = _split_pools(shortlist)

    if len(flex_pool) < 4 or len(food_pool) < 2:
        warnings.append(
            f"day{day_number} 동선 생성 불가 — 카페/활동 {len(flex_pool)}개(4 필요), "
            f"밥 {len(food_pool)}개(2 필요)"
        )
        return [], warnings

    start_coord, end_coord = _day_coords(day_info)

    start_candidates = list(flex_pool)
    random.shuffle(start_candidates)  # 동선마다 시작 장소를 다르게 하기 위한 순서 셔플

    routes: list[dict] = []
    seen_place_sets: set = set()

    for start_place in start_candidates:
        if len(routes) >= MAX_ROUTES_PER_DAY:
            break
        route = build_route(start_place, flex_pool, food_pool, transport, route_type, start_coord, end_coord)
        if route is None:
            continue
        place_set = frozenset(p["id"] for p in route["places"])
        if place_set in seen_place_sets:
            continue
        seen_place_sets.add(place_set)
        routes.append(route)

    routes.sort(key=lambda r: -r["total_score"])

    if len(routes) < MAX_ROUTES_PER_DAY:
        warnings.append(f"day{day_number} 동선 {len(routes)}개만 생성됨 (목표 {MAX_ROUTES_PER_DAY}개)")
    no_anchor = sum(1 for r in routes if not r["has_anchor"])
    if no_anchor:
        warnings.append(f"day{day_number} 앵커 미포함 동선 {no_anchor}/{len(routes)}개")

    return routes, warnings


# ─── [노드] 동선 후보 생성 ───
async def generate_route_candidates(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    transport  = ui.get("transport", "walk")
    route_type = ui.get("route_type", "only")
    days_info  = ui.get("days_info") or []
    day_info_map = {d["day_number"]: d for d in days_info}

    shortlist_by_day = state.get("shortlist_by_day") or {}

    if not shortlist_by_day:
        return {
            "route_candidates_by_day": {},
            "route_candidates":        [],
            "user_input":              ui,
            "warnings":                warnings + ["shortlist_by_day 없음 — enrich_and_score_places 점검 필요"],
            "step":                    "route_failed",
        }

    route_candidates_by_day: dict[int, list[dict]] = {}
    all_routes: list[dict] = []

    for day_number, shortlist in shortlist_by_day.items():
        day_info = day_info_map.get(day_number, {})
        routes, day_warnings = _build_day_routes(day_number, shortlist, day_info, transport, route_type)
        route_candidates_by_day[day_number] = routes
        all_routes.extend(routes)
        warnings.extend(day_warnings)

    return {
        "route_candidates_by_day": route_candidates_by_day,
        "route_candidates":        all_routes,
        "user_input":              ui,
        "warnings":                warnings,
        "step":                    "route_generated",
    }