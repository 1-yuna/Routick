# ─────────────────────────────────────────────────────────────────────
# first_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거
#      - 동행 유형 기반 제거
#      - 세부 카테고리별 중복 제한
#   2. 조건별 로직 수행 (pet 우선순위 처리)
#   3. 정렬 (음식점/카페 우선 + 활동 매칭 → 체인점 후순위)
#   4. 카테고리별 cap + 전체 cap 적용
#      - day 1개 기준 50개 고정
#      - 케이스 1 (only): 전체 cap = 50 × travelDays
#      - 케이스 2 (endpoint): day별 독립 적용 (day당 50개)
# ─────────────────────────────────────────────────────────────────────

from collections import Counter
from utils.first_filter.place_filter_pipeline import (
    filter_by_avoid,
    filter_by_irrelevant,
    filter_by_companion,
    filter_by_subcategory_cap,
    boost_pet_places,
    sort_by_priority,
    filter_by_category_cap,
    get_activity_keywords,
    DAY_FILTER_CAP,
    ONLY_FILTER_CAP,
)


# ─── 디버깅 헬퍼 ───
def _debug_print(label: str, places: list[dict], removed: int = 0) -> None:
    print(f"\n{label}")
    print(f"   {'─' * 50}")
    print(f"   ✂️  제거: {removed}개  |  남은: {len(places)}개")
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    dist   = "  ".join(f"{code}:{cnt}" for code, cnt in counts.most_common(6))
    print(f"   📊 카테고리: {dist}")
    if places:
        print("🔍 전체 장소 목록:")
        for idx, p in enumerate(places, start=1):
            code = p.get("category_group_code", "")
            name = p["name"]
            cat  = p.get("category", "")
            print(f"{idx:02}. [{code or '---':3}] {name} | {cat}")


def _debug_summary(label: str, places: list[dict]) -> None:
    print(f"\n{'═' * 60}")
    print(f"✅ {label}: {len(places)}개")
    print(f"{'═' * 60}")
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    for code, cnt in counts.most_common():
        bar = "█" * cnt
        print(f"   {code or '(없음)':6} {cnt:3}개  {bar}")


# ─── 단일 장소 목록 필터링 (day 1개분) ───
def _filter_one_day(
    places: list[dict],
    avoid_activities: list[str],
    companion_kr: str,
    activities_kr: list[str],
    route_type: str = "endpoint",
    travel_days: int = 1,
    debug: bool = False,
    day_label: str = "",
) -> list[dict]:
    activity_keywords = get_activity_keywords(activities_kr)

    if debug:
        _debug_print(f"📦 [{day_label}] 시작", places)

    # 1. avoid_activities 제거
    filtered, removed = filter_by_avoid(places, avoid_activities)
    if debug:
        _debug_print(f"1️⃣  [{day_label}] avoid_activities 필터", filtered, removed)

    # 2. 여행과 무관한 키워드 제거
    filtered, removed = filter_by_irrelevant(filtered)
    if debug:
        _debug_print(f"2️⃣  [{day_label}] 여행 무관 키워드 제거", filtered, removed)

    # 3. 동행 유형 기반 제거
    filtered, removed = filter_by_companion(filtered, companion_kr)
    if debug:
        _debug_print(f"3️⃣  [{day_label}] companion='{companion_kr}' 필터", filtered, removed)

    # 4. 세부 카테고리별 중복 제한 (동일 목적 장소 최대 2개)
    filtered, removed = filter_by_subcategory_cap(filtered, max_per_subcategory=2)
    if debug:
        _debug_print(f"4️⃣  [{day_label}] 세부 카테고리 중복 제한", filtered, removed)

    # 5. 정렬
    #    - 유저 선택 activity 키워드 매칭 → 앞으로
    #    - 반려동물과일 경우 펫 프렌들리 장소 우선 정렬
    #    - 프랜차이즈 → 뒤로
    if companion_kr == "반려동물과":
        filtered = boost_pet_places(filtered)
    filtered = sort_by_priority(filtered, activity_keywords)
    if debug:
        _debug_print(f"5️⃣  [{day_label}] 정렬", filtered, 0)

    # 3. cap 적용
    filtered, removed = filter_by_category_cap(filtered, travel_days=travel_days, route_type=route_type)
    if debug:
        _debug_print(f"3️⃣  [{day_label}] 카테고리 cap", filtered, removed)
        _debug_summary(f"최종 [{day_label}]", filtered)

    return filtered


# ─── [노드] 1차 필터링 ───
def first_filter_candidates(state: dict, debug: bool = False) -> dict:
    ui               = state["user_input"]
    candidates_by_day = state.get("candidates_by_day", {})
    warnings: list[str] = []

    route_type       = ui.get("route_type", "only")
    travel_days      = ui.get("travel_days", 1)
    companion_kr     = ui.get("companion_kr", "")
    avoid_activities = ui.get("avoid_activities") or []
    activities_kr    = ui.get("activities_kr") or []

    filtered_by_day:    dict[int, list] = {}
    all_filtered:       list[dict]      = []

    # 케이스 1 (only): 전체 candidates를 한 번 필터링
    # travel_days별 cap으로 하나의 풀 관리 (당일 50 / 1박2일 80 / 2박3일 100 / 3박4일 120)
    # plan_itinerary에서 day별 동선 생성 시 이전 day 선택 장소 제외
    if route_type == "only":
        all_candidates = state.get("candidates", [])
        total_cap = ONLY_FILTER_CAP.get(travel_days, ONLY_FILTER_CAP[1])["total"]

        filtered = _filter_one_day(
            places=all_candidates,
            avoid_activities=avoid_activities,
            companion_kr=companion_kr,
            activities_kr=activities_kr,
            route_type=route_type,
            travel_days=travel_days,
            debug=debug,
            day_label="only",
        )

        filtered = filtered[:total_cap]

        for day_number in range(1, travel_days + 1):
            filtered_by_day[day_number] = filtered

        all_filtered = filtered
        warnings.append(f"[only] filtered_candidates: {len(filtered)}개 (전 day 공유, cap={total_cap})")

    elif route_type == "endpoint":
        for day_number, day_candidates in candidates_by_day.items():
            filtered = _filter_one_day(
                places=day_candidates,
                avoid_activities=avoid_activities,
                companion_kr=companion_kr,
                activities_kr=activities_kr,
                route_type=route_type,
                travel_days=travel_days,
                debug=debug,
                day_label=f"day{day_number}",
            )
            filtered_by_day[day_number] = filtered
            all_filtered.extend(filtered)
            warnings.append(f"[endpoint] day{day_number} filtered_candidates: {len(filtered)}개")

    else:
        warnings.append(f"알 수 없는 route_type: {route_type}")

    return {
        "filtered_candidates": all_filtered,
        "filtered_by_day":     filtered_by_day,
        "user_input":          ui,
        "warnings":            warnings,
        "step":                "filtered",
    }