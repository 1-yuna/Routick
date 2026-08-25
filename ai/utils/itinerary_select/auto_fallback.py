# ─────────────────────────────────────────────────────────────────────
# auto_fallback
# ─────────────────────────────────────────────────────────────────────
# GPT 요청 실패(호출 실패 / 응답에 day 간 중복 존재) 시 폴백
#   - 날짜 간 장소가 중복되지 않는 후보 조합 중 우선순위(총점 합)가
#     가장 높은 조합을 자동 선택
#
# day별 유효 동선이 최대 5개(검증 통과분)라 day 4개여도 조합 수는 최대 5^4=625개 —
# 전수 탐색해도 비용이 거의 없음
# ─────────────────────────────────────────────────────────────────────

import itertools


# ─── 동선 하나의 장소 id 집합 ───
def _place_ids(route: dict) -> set[str]:
    return {p["id"] for p in route["places"]}


# ─── day 간 중복 없는 조합 중 총점 합이 가장 높은 조합 선택 ───
# valid_routes_by_day의 day 중 하나라도 후보가 0개면 애초에 조합 자체가 불가능 → None
def pick_best_combo(valid_routes_by_day: dict[int, list[dict]]) -> dict[int, dict] | None:
    day_numbers = sorted(valid_routes_by_day.keys())
    if any(not valid_routes_by_day[d] for d in day_numbers):
        return None

    candidate_lists = [valid_routes_by_day[d] for d in day_numbers]

    best_combo: dict[int, dict] | None = None
    best_score = -1.0

    for combo in itertools.product(*candidate_lists):
        seen: set[str] = set()
        has_dup = False
        for route in combo:
            ids = _place_ids(route)
            if seen & ids:
                has_dup = True
                break
            seen |= ids
        if has_dup:
            continue

        score = sum(route["total_score"] for route in combo)
        if score > best_score:
            best_score = score
            best_combo = {d: combo[i] for i, d in enumerate(day_numbers)}

    return best_combo