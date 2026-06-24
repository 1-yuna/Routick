# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 1차 필터링 함수 모음
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거
#      - 동행 유형 기반 제거
#      - 세부 카테고리별 중복 제한
#   2. 조건별 로직 수행 (pet 우선순위 처리)
#   3. 정렬
#      - 1단계: 유저 선택 활동 매칭 → 앞으로
#      - 2단계: 프랜차이즈 → 뒤로
#   4. cap 적용 (cafe 8 / food 12 / others 30 = 50개)
# ─────────────────────────────────────────────────────────────────────

from constants.place_keywords import (
    EXCLUDE_KEYWORDS,
    COMPANION_EXCLUDE_KEYWORDS,
    KEYWORD_EXPANSIONS,
)

# ─── day 1개 기준 카테고리별 cap (endpoint 케이스) ───
DAY_FILTER_CAP = 50  # endpoint 케이스: day당 고정
DAY_CATEGORY_CAP = {
    "CE7": 8,   # 카페
    "FD6": 12,  # 음식점
}
DAY_OTHERS_CAP = 30

# ─── only 케이스: travel_days별 전체 cap + 카테고리별 cap ───
ONLY_FILTER_CAP = {
    1: {"total": 50,  "CE7": 8,  "FD6": 12, "others": 30},
    2: {"total": 80,  "CE7": 13, "FD6": 19, "others": 48},
    3: {"total": 100, "CE7": 16, "FD6": 24, "others": 60},
    4: {"total": 120, "CE7": 19, "FD6": 29, "others": 72},
}
DAY_CATEGORY_CAP = {
    "CE7": 8,   # 카페
    "FD6": 12,  # 음식점
}
DAY_OTHERS_CAP = 30  # activity / 기타


# ─── avoid_activities 키워드 제거 ───
def filter_by_avoid(
        places: list[dict],
        avoid_activities: list[str],
) -> tuple[list[dict], int]:
    if not avoid_activities:
        return places, 0

    filtered = []
    for p in places:
        name     = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in avoid_activities):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 여행과 무관한 키워드 제거 ───
def filter_by_irrelevant(places: list[dict]) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        name     = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in EXCLUDE_KEYWORDS):
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
        name     = p.get("name", "")
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
        parts    = category.split(" > ")

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
    pet_keywords      = ["펫", "반려동물", "애견", "도그"]
    fallback_keywords = ["공원", "산책로"]

    pet_places = []
    others     = []

    for p in places:
        name     = p.get("name", "")
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


def is_chain_brand(place: dict) -> bool:
    name     = place.get("name", "")
    category = place.get("category", "")
    return any(brand in name or brand in category for brand in CHAIN_BRANDS)


# ─── 유저 선택 activity 확장 키워드 수집 ───
def get_activity_keywords(activities_kr: list[str]) -> list[str]:
    keywords = []
    for activity in activities_kr:
        expanded = KEYWORD_EXPANSIONS.get(activity, [])
        keywords.extend(expanded)
    return list(set(keywords))


# ─── 정렬
# 1단계: 유저 선택 활동 매칭 → 앞으로
# 2단계: 프랜차이즈 → 뒤로
# ───
def sort_by_priority(
        places: list[dict],
        activity_keywords: list[str] = None,
) -> list[dict]:
    if not activity_keywords:
        activity_keywords = []

    def priority(p):
        name     = p.get("name", "")
        category = p.get("category", "")
        matched  = bool(activity_keywords) and any(
            kw in name or kw in category for kw in activity_keywords
        )
        chain = is_chain_brand(p)

        if matched and not chain:  return 0  # 활동 매칭 + 비프랜차이즈
        if matched and chain:      return 1  # 활동 매칭 + 프랜차이즈
        if not chain:              return 2  # 비매칭 + 비프랜차이즈
        return 3                             # 비매칭 + 프랜차이즈 (맨 뒤)

    return sorted(places, key=priority)


# ─── cap 적용 ───
# endpoint 케이스: day당 고정 (cafe 8 / food 12 / others 30)
# only 케이스: travel_days별 단계적 확장
def filter_by_category_cap(
        places: list[dict],
        travel_days: int = 1,
        route_type: str = "endpoint",
) -> tuple[list[dict], int]:

    if route_type == "only":
        cap = ONLY_FILTER_CAP.get(travel_days, ONLY_FILTER_CAP[1])
        cafe_cap   = cap["CE7"]
        food_cap   = cap["FD6"]
        others_cap = cap["others"]
    else:
        cafe_cap   = DAY_CATEGORY_CAP["CE7"]
        food_cap   = DAY_CATEGORY_CAP["FD6"]
        others_cap = DAY_OTHERS_CAP

    cafe_count   = 0
    food_count   = 0
    others_count = 0
    filtered     = []

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
        else:
            if others_count >= others_cap:
                continue
            others_count += 1

        filtered.append(p)

    return filtered, len(places) - len(filtered)