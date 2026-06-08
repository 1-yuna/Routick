# ─────────────────────────────────────────────────────────────────────
# first_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates (travel_days 기반 동적 cap)
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거
#      - 연령대 기반 제거
#      - 동행 유형 기반 제거
#      - 세부 카테고리별 중복 제한
#   2. 조건별 로직 수행 (pet 우선순위 처리)
#   3. 정렬 (음식점/카페/숙소 우선 + 활동 매칭 → 체인점 후순위)
#   4. 카테고리별 cap + 전체 cap 적용
# ─────────────────────────────────────────────────────────────────────

from utils.first_filter.place_filter_pipeline import (
    filter_by_avoid,
    filter_by_irrelevant,
    filter_by_age,
    filter_by_companion,
    filter_by_subcategory_cap,
    boost_pet_places,
    sort_by_brand_priority,
    sort_by_priority,
    filter_by_category_cap,
    get_activity_keywords,
    FILTER_CAP,
)
from collections import Counter


# ─── 디버깅 헬퍼 ───
def _debug_print(label: str, places: list[dict], removed: int = 0) -> None:
    print(f"\n{label}")
    print(f"   {'─' * 50}")
    print(f"   ✂️  제거: {removed}개  |  남은: {len(places)}개")
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    dist = "  ".join(f"{code}:{cnt}" for code, cnt in counts.most_common(6))
    print(f"   📊 카테고리: {dist}")
    if places:
        print("🔍 전체 장소 목록:")
        for idx, p in enumerate(places, start=1):
            code = p.get("category_group_code", "")
            name = p["name"]
            cat = p.get("category", "")
            print(f"{idx:02}. [{code or '---':3}] {name} | {cat}")


def _debug_summary(places: list[dict]) -> None:
    print(f"\n{'═' * 60}")
    print(f"✅ 최종 filtered_candidates: {len(places)}개")
    print(f"{'═' * 60}")
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    print(f"\n📊 카테고리 분포:")
    for code, cnt in counts.most_common():
        bar = "█" * cnt
        print(f"   {code or '(없음)':6} {cnt:3}개  {bar}")
    chains = sum(1 for p in places if len(p.get("category", "").split(" > ")) >= 4)
    print(f"\n🏪 체인: {chains}개  |  🏠 로컬: {len(places) - chains}개")


# ─── [노드] 1차 필터링 ───
def first_filter_candidates(state: dict, debug: bool = False) -> dict:
    ui = state["user_input"]
    candidates = state["candidates"]
    warnings: list[str] = []

    travel_days = ui.get("travel_days", 1)
    companion_kr = ui.get("companion_kr", "")
    age_group = ui.get("age_group", "")
    avoid_activities = ui.get("avoid_activities") or []
    activities_kr = ui.get("activities_kr") or []
    max_count = FILTER_CAP.get(travel_days, 50)

    activity_keywords = get_activity_keywords(activities_kr)

    if debug:
        _debug_print("📦 시작", candidates)

    # ─── 1. 키워드 제거 ───
    # avoid_activities 제거
    filtered, removed = filter_by_avoid(candidates, avoid_activities)
    if removed > 0:
        warnings.append(f"avoid_activities 필터로 {removed}개 제거")
    if debug:
        _debug_print("1️⃣  avoid_activities 필터", filtered, removed)

    # 여행과 무관한 키워드 제거
    filtered, removed = filter_by_irrelevant(filtered)
    if removed > 0:
        warnings.append(f"여행과 무관한 키워드로 {removed}개 제거")
    if debug:
        _debug_print("2️⃣  여행과 무관한 키워드 제거", filtered, removed)

    # 연령대 기반 제거
    filtered, removed = filter_by_age(filtered, age_group)
    if removed > 0:
        warnings.append(f"{age_group} 연령대 부적합 키워드로 {removed}개 제거")
    if debug:
        _debug_print(f"3️⃣  age='{age_group}' 필터", filtered, removed)

    # 동행 유형 기반 제거
    filtered, removed = filter_by_companion(filtered, companion_kr)
    if removed > 0:
        warnings.append(f"{companion_kr} 부적합 키워드로 {removed}개 제거")
    if debug:
        _debug_print(f"4️⃣  companion='{companion_kr}' 필터", filtered, removed)

    # 세부 카테고리별 중복 제한
    filtered, removed = filter_by_subcategory_cap(filtered, max_per_subcategory=3)
    if removed > 0:
        warnings.append(f"세부 카테고리 중복 제한으로 {removed}개 제거")
    if debug:
        _debug_print("5️⃣  세부 카테고리 중복 제한", filtered, removed)

    # ─── 2. 조건별 로직 수행 ───
    if companion_kr == "반려동물과":
        filtered = boost_pet_places(filtered)
        warnings.append("반려동물과 → 펫 프렌들리 장소 우선 정렬")
        if debug:
            _debug_print("6️⃣  pet 우선순위 처리", filtered, 0)

    # ─── 3. 정렬 ───
    filtered = sort_by_priority(filtered, activity_keywords)
    if debug:
        _debug_print("7️⃣  우선순위 정렬", filtered, 0)

    filtered = sort_by_brand_priority(filtered)
    if debug:
        _debug_print("8️⃣  체인점 후순위 정렬", filtered, 0)

    # ─── 4. 카테고리별 cap + 전체 cap 적용 ───
    filtered, removed = filter_by_category_cap(filtered, travel_days, max_count)
    if removed > 0:
        warnings.append(f"카테고리 cap으로 {removed}개 제거")
    if debug:
        _debug_print("9️⃣  카테고리별 cap", filtered, removed)
        _debug_summary(filtered)

    warnings.append(f"최종 filtered_candidates: {len(filtered)}개")

    return {
        "filtered_candidates": filtered,
        "warnings": warnings,
        "step": "filtered",
    }