# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 1차 필터링 함수 모음
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

from constants.place_keywords import (
    EXCLUDE_KEYWORDS,
    COMPANION_EXCLUDE_KEYWORDS,
    AGE_EXCLUDE_KEYWORDS,
    KEYWORD_EXPANSIONS,
)


# ─── travel_days 기반 전체 cap ───
FILTER_CAP = {
    1: 50,
    2: 100,
    3: 150,
    4: 200,
}

# ─── travel_days 기반 카테고리별 cap ───
CATEGORY_CAP = {
    1: {"CE7": 10, "FD6": 10, "AD5": 0},
    2: {"CE7": 15, "FD6": 15, "AD5": 15},
    3: {"CE7": 20, "FD6": 20, "AD5": 20},
    4: {"CE7": 30, "FD6": 30, "AD5": 30},
}


# ─── avoid_activities 키워드 제거 ───
def filter_by_avoid(
        places: list[dict],
        avoid_activities: list[str],
) -> tuple[list[dict], int]:
    if not avoid_activities:
        return places, 0

    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in avoid_activities):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 여행과 무관한 키워드 제거 ───
def filter_by_irrelevant(places: list[dict]) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in EXCLUDE_KEYWORDS):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 연령대 기반 제거 ───
def filter_by_age(
        places: list[dict],
        age_group: str,
) -> tuple[list[dict], int]:
    exclude_keywords = AGE_EXCLUDE_KEYWORDS.get(age_group, [])

    if not exclude_keywords:
        return places, 0

    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in exclude_keywords):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 동행 유형 기반 제거 ───
def filter_by_companion(
        places: list[dict],
        companion: str,
) -> tuple[list[dict], int]:
    exclude_keywords = COMPANION_EXCLUDE_KEYWORDS.get(companion, [])

    if not exclude_keywords:
        return places, 0

    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in exclude_keywords):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 세부 카테고리별 중복 제한 ───
def filter_by_subcategory_cap(
        places: list[dict],
        max_per_subcategory: int = 3,
) -> tuple[list[dict], int]:
    subcategory_count = {}
    filtered = []

    for p in places:
        category = p.get("category", "")
        parts = category.split(" > ")

        # 3단계 이상이면 2~3번째 카테고리 조합으로 체크
        # 예) "스포츠,레저 > 골프 > 골프연습장 > 스크린골프연습장 > 골프존파크"
        #     → "골프 > 골프연습장" 으로 체크
        if len(parts) >= 3:
            subcategory = " > ".join(parts[1:3])
        elif len(parts) == 2:
            subcategory = parts[1]
        else:
            subcategory = category

        count = subcategory_count.get(subcategory, 0)
        if count >= max_per_subcategory:
            continue

        subcategory_count[subcategory] = count + 1
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── pet 우선순위 처리 ───
def boost_pet_places(places: list[dict]) -> list[dict]:
    pet_keywords = ["펫", "반려동물", "애견", "도그"]
    fallback_keywords = ["공원", "산책로"]

    pet_places = []
    others = []

    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in pet_keywords):
            pet_places.append(p)
        else:
            others.append(p)

    if not pet_places:
        fallback = [p for p in others if any(
            kw in p.get("name", "") or kw in p.get("category", "")
            for kw in fallback_keywords
        )]
        rest = [p for p in others if p not in fallback]
        return fallback + rest

    return pet_places + others


# ─── 체인 브랜드 목록 ───
CHAIN_BRANDS = [
    "스타벅스", "메가MGC커피", "투썸플레이스", "이디야", "빽다방",
    "CGV", "롯데시네마", "메가박스", "설빙", "파리바게뜨",
    "뚜레쥬르", "맥도날드", "버거킹", "롯데리아", "KFC",
]


# ─── 체인점 후순위 정렬 ───
def is_chain_brand(place: dict) -> bool:
    category = place.get("category", "")
    name = place.get("name", "")
    return any(brand in category or brand in name for brand in CHAIN_BRANDS)


def sort_by_brand_priority(places: list[dict]) -> list[dict]:
    locals_ = [p for p in places if not is_chain_brand(p)]
    chains = [p for p in places if is_chain_brand(p)]
    return locals_ + chains


# ─── 유저 선택 activity 확장 키워드 수집 ───
def get_activity_keywords(activities_kr: list[str]) -> list[str]:
    keywords = []
    for activity in activities_kr:
        expanded = KEYWORD_EXPANSIONS.get(activity, [])
        keywords.extend(expanded)
    return list(set(keywords))


# ─── 음식점/카페/숙소 우선 + 유저 선택 activity 키워드 매칭 정렬 ───
def sort_by_priority(places: list[dict], activity_keywords: list[str] = None) -> list[dict]:
    if activity_keywords is None:
        activity_keywords = []

    def priority(p):
        code = p.get("category_group_code", "")
        name = p.get("name", "")
        category = p.get("category", "")

        if code == "FD6":   # 음식점 최우선
            return 0
        if code == "CE7":   # 카페 2순위
            return 1
        if code == "AD5":   # 숙소 3순위
            return 2
        if activity_keywords and any(
            kw in name or kw in category for kw in activity_keywords
        ):
            return 3        # 유저 선택 활동 매칭 장소
        return 4            # 나머지

    return sorted(places, key=priority)


# ─── 카테고리별 cap + 전체 cap 적용 ───
def filter_by_category_cap(
        places: list[dict],
        travel_days: int,
        max_count: int,
) -> tuple[list[dict], int]:
    cap = CATEGORY_CAP.get(travel_days, CATEGORY_CAP[1])

    cafe_cap = cap["CE7"]
    food_cap = cap["FD6"]
    lodging_cap = cap["AD5"]
    others_cap = max_count - cafe_cap - food_cap - lodging_cap

    cafe_count = 0
    food_count = 0
    lodging_count = 0
    others_count = 0
    filtered = []

    for p in places:
        code = p.get("category_group_code", "")

        if code == "CE7":
            if cafe_count >= cafe_cap:
                continue
            cafe_count += 1
        elif code == "FD6":
            if food_count >= food_cap:
                continue
            food_count += 1
        elif code == "AD5":
            if lodging_count >= lodging_cap:
                continue
            lodging_count += 1
        else:
            if others_count >= others_cap:
                continue
            others_count += 1

        filtered.append(p)

    return filtered, len(places) - len(filtered)