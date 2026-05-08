# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 관련 없는 키워드 제거 함수
#
# 흐름:
#   1. dislike 키워드 제거
#   2. 부적합 키워드 제거
#   3. 구성원에 따라 부적합 키워드 제거
#   4. 당일치기 경우 숙박 제거
#   5. 체인 브랜드 후순위
#   6. 카페,음식점 우선 순위로 바꾼 뒤 (필수적으로 포함되어야하기 때문) > 카페, 음식점 수 줄이기
# ─────────────────────────────────────────────────────────────────────
from constants.keywords import EXCLUDE_KEYWORDS, PARTY_EXCLUDE_KEYWORDS


# ─── dislike 키워드 제거 ───
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


# ─── 부적합 키워드 제거 ───
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


# ─── 구성원에 따라 부적합 키워드 제거 ───
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


# ─── 당일이면 숙박 제거 ───
def filter_by_accommodation(places: list[dict]) -> tuple[list[dict], int]:
    filtered = [p for p in places if p.get("category_group_code") != "AD5"]
    removed = len(places) - len(filtered)
    return filtered, removed


# 카테고리 depth가 4개면 체인 브랜드로 판단
def is_chain_brand(category: str) -> bool:
    return len(category.split(" > ")) >= 4

# ─── 체인점 후순위 ───
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


# ─── 음식점/카페 우선 정렬 ───
def sort_by_priority(places: list[dict]) -> list[dict]:
    def priority(p):
        code = p.get("category_group_code", "")
        if code == "FD6":   # 음식점 최우선
            return 0
        if code == "CE7":   # 카페 2순위
            return 1
        return 2            # 나머지
    return sorted(places, key=priority)


# ─── 카페, 음식점 개수 줄이기 ───
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
