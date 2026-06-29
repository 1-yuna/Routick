# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# 동선 후보 중 상위 N개 추출 + 주차장 추가 + fallback
#
# 흐름:
#   1. 중복 동선 제거 (유사도 70% 이상)
#   2. total_score 내림차순 정렬 후 day별 상위 5개 반환
#   3. 최종 후보 수 검증 (3개 미만이면 fallback)
#      - 이동시간 초과 기준 완화 후 generate_candidates 재실행
#      - fallback도 미달이면 전체 동선 사용
# ─────────────────────────────────────────────────────────────────────

# ─── day별 최대 동선 수 ───
MAX_ITINERARIES_PER_DAY = 5

# ─── fallback 시 완화 기준 ───
FALLBACK_TRAVEL_LIMIT_ADD = 10


# ─── 동선 유사도 계산 ───
def similarity(itin1: list[dict], itin2: list[dict]) -> float:
    ids1 = set(item["place"]["id"] for item in itin1)
    ids2 = set(item["place"]["id"] for item in itin2)
    intersection = ids1 & ids2
    union        = ids1 | ids2
    return len(intersection) / len(union) if union else 0


# ─── [노드] 일정 계획 리스트 작성 ───
def plan_itinerary(state: dict) -> dict:
    valid_routes_by_day = state.get("valid_routes_by_day", {})
    all_routes_by_day   = state.get("all_routes_by_day", {})
    warnings: list[str] = []

    itineraries_by_day: dict[int, list[list[dict]]] = {}
    used_place_ids: set[str] = set()

    for day_number in sorted(valid_routes_by_day.keys()):
        valid_routes = valid_routes_by_day[day_number]
        all_routes   = all_routes_by_day.get(day_number, [])

        # fallback: 유효 동선 3개 미만이면 전체 동선 사용
        if len(valid_routes) < 3:
            warnings.append(f"day{day_number} 유효 동선 {len(valid_routes)}개 → 전체 동선 사용")
            valid_routes = all_routes

        if not valid_routes:
            warnings.append(f"day{day_number} 동선 없음 → 스킵")
            continue

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

        # 다음 day에서 제외할 장소 누적
        for route in top_routes:
            for item in route["itinerary"]:
                used_place_ids.add(item["place"]["id"])

    return {
        "itineraries_by_day": itineraries_by_day,
        "warnings":           warnings,
        "step":               "itinerary_planned",
    }