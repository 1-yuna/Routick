# ─────────────────────────────────────────────────────────────────────
# first_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거 (category: EXCLUDE_KEYWORDS, name: EXCLUDE_KEYWORDS_NAME)
#      - activities 선택 여부 기반 제거 (category: ACTIVITY_EXCLUDE_KEYWORDS)
#      - 세부 카테고리별 중복 제한 (동일 카테고리 최대 2개)
#   2. 정렬
#      - 활동/동행자별 장소 우선 정렬 (PRIORITY_KEYWORDS)
#      - final_keywords category 매칭 → 최우선
#      - name_search_keywords name 매칭 → 다음
#      - 프랜차이즈 → 뒤로
#   3. 경로 인접성 정렬 (endpoint 전용)
#      - start~end 직선 경로에서 수직 거리가 먼 activity/browse/pop 장소를 뒤로 정렬
#      - food/cafe(FD6/CE7)는 거리와 무관하게 우선순위 유지
#   4. 카테고리별 cap + 전체 cap 적용
#      - 케이스 1 (only): K-means 지리 분할 후 day당 50개
#      - 케이스 2 (endpoint): day별 독립 적용 (day당 50개), 이전 day 장소 제외
# ─────────────────────────────────────────────────────────────────────

from collections import Counter
from utils.first_filter.place_filter_pipeline import (
    filter_by_avoid,
    filter_by_irrelevant,
    filter_by_activity_exclude,
    filter_by_subcategory_cap,
    filter_by_bucket_and_activity,
    boost_by_priority,
    sort_by_priority,
    sort_by_route_proximity,
    filter_by_category_cap,
    get_activity_keywords,
    DAY_FILTER_CAP,
    ONLY_FILTER_CAP,
)


# ─── 브랜드명 정규화 (지점 suffix 제거) ───
def _brand_name(name: str) -> str:
    """'수변최고돼지국밥 광안리점' → '수변최고돼지국밥'
    마지막 토큰이 지점 suffix로 끝나면 제거."""
    import re
    name = name.strip()
    name = re.sub(r'\s+\S*(점|지점|호점|본점|직영점|분점)$', '', name)
    return name.strip()


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
    final_keywords: list[str],
    name_search_keywords: list[str],
    warnings: list[str],
    route_type: str = "endpoint",
    travel_days: int = 1,
    debug: bool = False,
    day_label: str = "",
    start_lat: float = None,
    start_lng: float = None,
    end_lat: float = None,
    end_lng: float = None,
) -> list[dict]:
    activity_keywords = get_activity_keywords(activities_kr)

    if debug:
        _debug_print(f"📦 [{day_label}] 시작", places)

    filtered, removed = filter_by_avoid(places, avoid_activities)
    if debug:
        _debug_print(f"1️⃣  [{day_label}] avoid_activities 필터", filtered, removed)

    filtered, removed = filter_by_irrelevant(filtered)
    if debug:
        _debug_print(f"2️⃣  [{day_label}] 여행 무관 키워드 제거", filtered, removed)

    filtered, removed = filter_by_activity_exclude(filtered, activities_kr)
    if debug:
        _debug_print(f"3️⃣  [{day_label}] activity 기반 제거 필터", filtered, removed)

    filtered, removed = filter_by_subcategory_cap(filtered, max_per_subcategory=2)
    if debug:
        _debug_print(f"4️⃣  [{day_label}] 세부 카테고리 중복 제한", filtered, removed)

    filtered, removed = filter_by_bucket_and_activity(filtered, activity_keywords)
    if removed > 0:
        warnings.append(f"[{day_label}] activity 필터로 {removed}개 제거")
    if debug:
        _debug_print(f"5️⃣  [{day_label}] bucket 분류 + activity 필터", filtered, removed)

    filtered = boost_by_priority(filtered, companion_kr=companion_kr, activities_kr=activities_kr)
    filtered = sort_by_priority(filtered, final_keywords=final_keywords, name_search_keywords=name_search_keywords)
    if debug:
        _debug_print(f"5️⃣  [{day_label}] 정렬", filtered, 0)

    if route_type == "endpoint" and None not in (start_lat, start_lng, end_lat, end_lng):
        food_cafe = [p for p in filtered if p.get("category_group_code") in ("FD6", "CE7")]
        other     = [p for p in filtered if p.get("category_group_code") not in ("FD6", "CE7")]
        other     = sort_by_route_proximity(other, start_lat, start_lng, end_lat, end_lng)
        filtered  = food_cafe + other
        if debug:
            _debug_print(f"6️⃣  [{day_label}] 경로 인접성 정렬", filtered, 0)

    filtered, removed = filter_by_category_cap(filtered, travel_days=travel_days, route_type=route_type)
    if debug:
        _debug_print(f"7️⃣  [{day_label}] 카테고리 cap", filtered, removed)
        _debug_summary(f"최종 [{day_label}]", filtered)

    return filtered


# ─── [노드] 1차 필터링 ───
def first_filter_candidates(state: dict, debug: bool = False) -> dict:
    ui                = state["user_input"]
    candidates_by_day = state.get("candidates_by_day", {})
    warnings: list[str] = []

    route_type           = ui.get("route_type", "only")
    travel_days          = ui.get("travel_days", 1)
    companion_kr         = ui.get("companion_kr", "")
    avoid_activities     = ui.get("avoid_activities") or []
    activities_kr        = ui.get("activities_kr") or []
    final_keywords       = ui.get("final_keywords") or []
    name_search_keywords = ui.get("name_search_keywords") or []

    filtered_by_day: dict[int, list] = {}
    all_filtered:    list[dict]      = []

    # ── 케이스 1 (only): 정렬 후 라운드로빈으로 day별 균등 배분 ──────────
    if route_type == "only":
        all_candidates = candidates_by_day.get(1, [])

        # 우선순위 정렬 (활동/동행자 우선 + 프랜차이즈 뒤로)
        sorted_candidates = boost_by_priority(all_candidates, companion_kr=companion_kr, activities_kr=activities_kr)
        sorted_candidates = sort_by_priority(sorted_candidates, final_keywords=final_keywords, name_search_keywords=name_search_keywords)

        # category_group_code 기준 분류 (food/cafe/others)
        food_list   = [p for p in sorted_candidates if p.get("category_group_code") == "FD6"]
        cafe_list   = [p for p in sorted_candidates if p.get("category_group_code") == "CE7"]
        others_list = [p for p in sorted_candidates if p.get("category_group_code") not in ("FD6", "CE7")]

        # 라운드로빈: 정렬된 순서대로 day1, day2, ..., day1, day2... 순환 배분
        def _round_robin(items: list, n: int) -> dict[int, list]:
            groups: dict[int, list] = {i: [] for i in range(n)}
            for idx, item in enumerate(items):
                groups[idx % n].append(item)
            return groups

        food_groups   = _round_robin(food_list, travel_days)
        cafe_groups   = _round_robin(cafe_list, travel_days)
        others_groups = _round_robin(others_list, travel_days)

        for day_number in range(1, travel_days + 1):
            day_idx = day_number - 1
            day_candidates = (
                food_groups[day_idx] + cafe_groups[day_idx] + others_groups[day_idx]
            )

            filtered = _filter_one_day(
                places=day_candidates,
                avoid_activities=avoid_activities,
                companion_kr=companion_kr,
                activities_kr=activities_kr,
                final_keywords=final_keywords,
                name_search_keywords=name_search_keywords,
                warnings=warnings,
                route_type="only_day",
                travel_days=travel_days,
                debug=debug,
                day_label=f"only-day{day_number}",
            )

            filtered_by_day[day_number] = filtered
            all_filtered.extend(filtered)
            warnings.append(f"[only] day{day_number} filtered_candidates: {len(filtered)}개 (cluster{day_number-1})")

    # ── 케이스 2 (endpoint): day별 독립 처리, 이전 day 장소 제외 ────────
    elif route_type == "endpoint":
        used_place_ids: set[str] = set()
        used_brand_names: set[str] = set()
        days_raw = ui.get("days") or []

        for day_number in sorted(candidates_by_day.keys()):
            day_candidates = candidates_by_day[day_number]

            day_candidates = [
                p for p in day_candidates
                if p["id"] not in used_place_ids
                and _brand_name(p["name"]) not in used_brand_names
            ]

            day_raw   = next((d for d in days_raw if d.get("day_number") == day_number), None)
            start_lat = day_raw.get("start_lat") if day_raw else None
            start_lng = day_raw.get("start_lng") if day_raw else None
            end_lat   = day_raw.get("end_lat") if day_raw else None
            end_lng   = day_raw.get("end_lng") if day_raw else None

            filtered = _filter_one_day(
                places=day_candidates,
                avoid_activities=avoid_activities,
                companion_kr=companion_kr,
                activities_kr=activities_kr,
                final_keywords=final_keywords,
                name_search_keywords=name_search_keywords,
                warnings=warnings,
                route_type=route_type,
                travel_days=travel_days,
                debug=debug,
                day_label=f"day{day_number}",
                start_lat=start_lat,
                start_lng=start_lng,
                end_lat=end_lat,
                end_lng=end_lng,
            )

            for p in filtered:
                used_place_ids.add(p["id"])
                used_brand_names.add(_brand_name(p["name"]))

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