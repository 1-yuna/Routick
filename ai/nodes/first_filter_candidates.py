# ─────────────────────────────────────────────────────────────────────
# filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates (최대 50개)
#
# 흐름:
#   1. dislike 키워드 제거
#   2. 관련 없는 키워드 제거
#   3. 구성원에 따라 키워드 제거
#   4. 당일치기 -> 숙박 제거
#   5. 체인 브랜드 후순위
#   6. 카페, 음식점 수 줄이기
# ─────────────────────────────────────────────────────────────────────

from constants.keywords import EXCLUDE_KEYWORDS, PARTY_EXCLUDE_KEYWORDS
# ─── 디버깅 헬퍼 (배포 시 제거 또는 debug=False) ───
from collections import Counter


def _debug_print(label: str, places: list[dict], removed: int = 0) -> None:
    """필터 단계별 결과 출력."""
    print(f"\n{label}")
    print(f"   {'─' * 50}")
    print(f"   ✂️  제거: {removed}개  |  남은: {len(places)}개")

    # 카테고리 그룹 분포
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
    """최종 결과 요약."""
    print(f"\n{'═' * 60}")
    print(f"✅ 최종 filtered_candidates: {len(places)}개")
    print(f"{'═' * 60}")

    # 전체 카테고리 분포
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    print(f"\n📊 카테고리 분포:")
    for code, cnt in counts.most_common():
        bar = "█" * cnt
        print(f"   {code or '(없음)':6} {cnt:3}개  {bar}")

    # 체인 vs 로컬 분포
    chains = sum(1 for p in places if len(p.get("category", "").split(" > ")) >= 4)
    print(f"\n🏪 체인: {chains}개  |  🏠 로컬: {len(places) - chains}개")


# 1) dislike 키워드 제거
def filter_by_dislike(
        places: list[dict],
        dislike_keywords: list[str],
) -> tuple[list[dict], int]:

    if not dislike_keywords:
        return places, 0

    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")

        # dislike 키워드 중 하나라도 이름/카테고리에 들어있으면 제외
        if any(kw in name or kw in category for kw in dislike_keywords):
            continue

        filtered.append(p)

    removed = len(places) - len(filtered)
    return filtered, removed


# 2) 추천에 안 맞는 키워드 제거
def filter_by_irrelevant(places: list[dict]) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        # 키워드로 제외
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in EXCLUDE_KEYWORDS):
            continue

        filtered.append(p)

    return filtered, len(places) - len(filtered)


# 3) 구성원 기반 키워드 제거
def filter_by_party(
        places: list[dict],
        party: str,
) -> tuple[list[dict], int]:

    exclude_keywords = PARTY_EXCLUDE_KEYWORDS.get(party, [])

    if not exclude_keywords:
        return places, 0

    filtered = []

    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")

        if any(
                kw in name or kw in category
                for kw in exclude_keywords
        ):
            continue

        filtered.append(p)

    removed = len(places) - len(filtered)
    return filtered, removed


# 4) 당일이면 숙박 제거
def filter_by_accommodation(places: list[dict]) -> tuple[list[dict], int]:
    filtered = [p for p in places if p.get("category_group_code") != "AD5"]
    removed = len(places) - len(filtered)
    return filtered, removed


# 카테고리 depth가 4개면 체인 브랜드로 판단
def is_chain_brand(category: str) -> bool:
    return len(category.split(" > ")) >= 4


# 5) 체인점 후순위
def filter_by_brand_priority(
        places: list[dict],
        max_count: int = 50,
) -> tuple[list[dict], int]:
    locals_ = [p for p in places if not is_chain_brand(p.get("category", ""))]
    chains = [p for p in places if is_chain_brand(p.get("category", ""))]

    # 로컬 먼저 채우고 자리 남으면 체인 추가
    result = locals_[:]
    remaining = max_count - len(result)
    if remaining > 0:
        result += chains[:remaining]

    removed = len(places) - len(result)
    return result, removed

# 5.5) 음식점/카페 우선 정렬
def sort_by_priority(places: list[dict]) -> list[dict]:
    def priority(p):
        code = p.get("category_group_code", "")
        if code == "FD6":   # 음식점 최우선
            return 0
        if code == "CE7":   # 카페 2순위
            return 1
        return 2            # 나머지
    return sorted(places, key=priority)


# 6) 카페, 음식점 개수 줄이기
def filter_by_category_cap(
        places: list[dict],
        activity_preferences: list[str],
) -> tuple[list[dict], int]:
    # cap 설정
    cafe_cap = 10 if "카페" in activity_preferences else 5
    food_cap = 20
    gym_cap = 5 if "헬스" in activity_preferences else 1
    pc_cap = 5 if "PC방" in activity_preferences else 1

    cafe_count = 0
    food_count = 0
    gym_count = 0
    pc_count = 0
    filtered = []

    for p in places:
        code = p.get("category_group_code", "")
        name = p.get("name", "")
        category = p.get("category", "")

        if code == "CE7":  # 카페 먼저 체크
            if cafe_count >= cafe_cap:
                continue
            cafe_count += 1

        elif code == "FD6":  # 음식점은 CE7 아닐 때만
            if food_count >= food_cap:
                continue
            food_count += 1

        elif "헬스" in name or "피트니스" in name or "필라테스" in name or "헬스" in category or "피트니스" in category:
            if gym_count >= gym_cap:
                continue
            gym_count += 1

        elif "PC방" in name or "PC방" in category:
            if pc_count >= pc_cap:
                continue
            pc_count += 1

        filtered.append(p)

    removed = len(places) - len(filtered)
    return filtered, removed


# [메인] 필터
def first_filter_candidates(state: dict, debug: bool = False) -> dict:
    ui = state["user_input"]
    candidates = state["candidates"]
    warnings: list[str] = []
    if debug:
        _debug_print("📦 시작", candidates)

    # ─── 1. dislike 필터 ───
    dislike_keywords = ui.get("dislike_keywords") or []
    filtered, removed_dislike = filter_by_dislike(candidates, dislike_keywords)

    if removed_dislike > 0:
        warnings.append(f"dislike 필터로 {removed_dislike}개 제거")

    if debug:
        _debug_print(f"1️⃣  dislike 필터 ({dislike_keywords})", filtered, removed_dislike)

    # ─── 2. 관련 없는 키워드 필터 (시스템 기본) ───
    filtered, removed = filter_by_irrelevant(filtered)
    if removed > 0:
        warnings.append(f"부적합 카테고리로 {removed}개 제거")
    if debug:
        _debug_print("2️⃣  부적합 카테고리", filtered, removed)

    # ─── 3. 구성원 기반 필터 ───
    party = ui.get("party_type")
    filtered, removed = filter_by_party(filtered, party)
    if removed > 0:
        warnings.append(f"{party} 부적합 키워드로 {removed}개 제거")
    else :
        warnings.append(f"부적합 키워드로 0개 제거")
    if debug:
        _debug_print(f"3️⃣  party='{party}' 필터", filtered, removed)

    # ─── 4. 당일치기 숙박 필터 ───
    if ui.get("duration") == "당일":
        filtered, removed = filter_by_accommodation(filtered)
        if removed > 0:
            warnings.append(f"당일치기로 숙박 {removed}개 제거")
        if debug:
            _debug_print("4️⃣  당일치기 숙박 제거", filtered, removed)

    # ─── 5. 로컬 우선, 체인 후순위 ───
    filtered, removed = filter_by_brand_priority(filtered, max_count=50)
    if removed > 0:
        warnings.append(f"체인점 후순위 처리로 {removed}개 제거")
    if debug:
        _debug_print("5️⃣  체인점 후순위 (50 cap)", filtered, removed)

    # ─── 5.5 음식점/카페 우선 정렬 ───
    filtered = sort_by_priority(filtered)
    if debug:
        _debug_print("5️⃣ ½ 음식점/카페 우선순위 정렬", filtered, 0)

    # ─── 6. 카페, 음식점 줄이기 ───
    activity_preferences = ui.get("activity_preferences") or []
    needs_meal = ui.get("needs_meal") or False
    filtered, removed = filter_by_category_cap(filtered, activity_preferences)
    if removed > 0:
        warnings.append(f"카페,음식점 {removed}개 제거")
    if debug:
        _debug_print("6️⃣  카페,음식점 cap", filtered, removed)

    # ─── 7. 50개 cap ───
    if len(filtered) > 50:
        warnings.append(f"50개로 cap (원본 {len(filtered)}개)")
        filtered = filtered[:50]
    else:
        warnings.append(f"원본 {len(filtered)}개")
    if debug:
        _debug_print("6️⃣  50개로 cap", filtered, removed)
    if debug:
        _debug_summary(filtered)

    return {
        "filtered_candidates": filtered,
        "warnings": warnings,
        "step": "filtered",
    }