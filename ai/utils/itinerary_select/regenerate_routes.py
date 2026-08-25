# ─────────────────────────────────────────────────────────────────────
# regenerate_routes
# ─────────────────────────────────────────────────────────────────────
# 검증 실패(유효 동선 0개) day 롤백 — 조건 완화 재생성
#   - shortlist quota 20개 → 30개로 확대
#     (블로그/GPT 재호출 없이 enrich_and_score_places가 이미 만들어둔
#      scored_by_day에서 quota만 다시 잘라 씀)
#   - 검증에서 걸린 장소(failed_place_ids) 제외
#   - 슬롯 6개 → 5개로 축소 (카페·활동→밥→카페·활동→밥→카페·활동)
#     시간 예산 초과로 실패하는 경우를 줄이기 위한 완화
# ─────────────────────────────────────────────────────────────────────

import random

from utils.enrich_score.score_filter import select_day_shortlist
from utils.route.route_build import build_route, SLOT_PATTERN_5

from utils.itinerary_select.validate_routes import validate_route

ROLLBACK_QUOTA = {"food": 10, "cafe": 5, "activity": 15}
MAX_ROUTES_PER_DAY = 5


# ─── shortlist를 bucket별 풀로 분리 (generate_route_candidates.py와 동일 로직) ───
def _split_pools(shortlist: list[dict]) -> tuple[list[dict], list[dict]]:
    flex_pool = [p for p in shortlist if p.get("bucket") in ("cafe", "activity")]
    food_pool = [p for p in shortlist if p.get("bucket") == "food"]
    return flex_pool, food_pool


# ─── day_info에서 mid/start/end 좌표 추출 (generate_route_candidates.py와 동일 로직) ───
def _day_coords(day_info: dict) -> tuple:
    start_lat, start_lng = day_info.get("start_lat"), day_info.get("start_lng")
    end_lat, end_lng     = day_info.get("end_lat"), day_info.get("end_lng")
    start_coord = (start_lat, start_lng) if start_lat is not None and start_lng is not None else None
    end_coord   = (end_lat, end_lng) if end_lat is not None and end_lng is not None else None
    return start_coord, end_coord


# ─── day 하나: 완화된 조건(30개 후보, 5슬롯)으로 재생성 + 재검증까지 마친 유효 동선 반환 ───
def regenerate_day(
    day_number: int,
    day_scored: list[dict],
    failed_place_ids: set[str],
    day_info: dict,
    transport: str,
    route_type: str,
    budget_minutes: int,
) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []

    pool = [p for p in day_scored if p["id"] not in failed_place_ids]
    shortlist30 = select_day_shortlist(pool, quota=ROLLBACK_QUOTA)
    flex_pool, food_pool = _split_pools(shortlist30)

    if len(flex_pool) < 3 or len(food_pool) < 2:
        warnings.append(
            f"day{day_number} 롤백 재생성 불가 — 카페/활동 {len(flex_pool)}개(3 필요), "
            f"밥 {len(food_pool)}개(2 필요, 실패 장소 {len(failed_place_ids)}개 제외 후)"
        )
        return [], warnings

    start_coord, end_coord = _day_coords(day_info)

    start_candidates = list(flex_pool)
    random.shuffle(start_candidates)

    routes: list[dict] = []
    seen_place_sets: set = set()

    for start_place in start_candidates:
        if len(routes) >= MAX_ROUTES_PER_DAY:
            break
        route = build_route(
            start_place, flex_pool, food_pool, transport, route_type, start_coord, end_coord,
            slot_pattern=SLOT_PATTERN_5,
        )
        if route is None:
            continue
        place_set = frozenset(p["id"] for p in route["places"])
        if place_set in seen_place_sets:
            continue
        if validate_route(route, budget_minutes) is not None:
            continue
        seen_place_sets.add(place_set)
        routes.append(route)

    routes.sort(key=lambda r: -r["total_score"])

    if not routes:
        warnings.append(f"day{day_number} 롤백 재생성 후에도 유효 동선 0개")
    elif len(routes) < MAX_ROUTES_PER_DAY:
        warnings.append(f"day{day_number} 롤백 재생성 — 동선 {len(routes)}개 (5슬롯, quota 30)")
    else:
        warnings.append(f"day{day_number} 롤백 재생성 성공 — 동선 {len(routes)}개 (5슬롯, quota 30)")

    return routes, warnings