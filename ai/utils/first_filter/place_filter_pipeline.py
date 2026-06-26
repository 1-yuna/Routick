# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 1차 필터링 함수 모음
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거 (category: EXCLUDE_KEYWORDS, name: EXCLUDE_KEYWORDS_NAME)
#      - 활동/동행 유형 기반 제거 (COMPANION_EXCLUDE_KEYWORDS)
#      - 세부 카테고리별 중복 제한 (동일 카테고리 최대 2개)
#   2. 정렬
#      - 활동/동행자별 장소 우선 정렬 (PRIORITY_KEYWORDS)
#      - 유저 선택 activity 키워드 매칭 → 앞으로
#      - 프랜차이즈 → 뒤로
#   3. cap 적용
# ─────────────────────────────────────────────────────────────────────

from constants.place_keywords import (
    EXCLUDE_KEYWORDS,
    EXCLUDE_KEYWORDS_NAME,
    ACTIVITY_EXCLUDE_KEYWORDS,
    KEYWORD_EXPANSIONS,
    PRIORITY_KEYWORDS,
)

# ─── day 1개 기준 카테고리별 cap (endpoint 케이스) ───
DAY_FILTER_CAP = 50
DAY_CATEGORY_CAP = {
    "CE7": 8,
    "FD6": 12,
}
DAY_OTHERS_CAP = 30

# ─── only 케이스: travel_days별 전체 cap + 카테고리별 cap ───
ONLY_FILTER_CAP = {
    1: {"total": 50,  "CE7": 8,  "FD6": 12, "others": 30},
    2: {"total": 80,  "CE7": 13, "FD6": 19, "others": 48},
    3: {"total": 100, "CE7": 16, "FD6": 24, "others": 60},
    4: {"total": 120, "CE7": 19, "FD6": 29, "others": 72},
}

# ─── 체험형 카페 키워드 (CE7이지만 activity로 분류) ───
ACTIVITY_CAFE_KEYWORDS = [
    "보드카페", "만화카페", "만화방", "방탈출", "방탈출카페",
    "애견카페", "고양이카페", "동물카페", "VR카페",
]

# ─── 베이커리/제과/디저트 키워드 (FD6이지만 cafe로 분류) ───
CAFE_FOOD_KEYWORDS = ["제과", "베이커리", "디저트"]


# ─── bucket 예비 분류 ───
def classify_bucket(place: dict) -> str:
    code     = place.get("category_group_code", "")
    name     = place.get("name", "") or ""
    category = place.get("category", "") or ""

    if code == "CE7":
        if any(kw in category or kw in name for kw in ACTIVITY_CAFE_KEYWORDS):
            return "activity"
        return "cafe"
    if code == "FD6":
        if any(kw in category for kw in CAFE_FOOD_KEYWORDS):
            return "cafe"
        return "food"
    if code in ("AT4", "CT1"):
        return "activity"
    # category 텍스트로 판단
    if any(kw in category for kw in ["음식점", "한식", "양식", "일식", "중식", "분식"]):
        return "food"
    if "카페" in category:
        return "cafe"
    if any(kw in category for kw in ["관광", "문화", "전시", "박물", "체험", "스포츠", "레저", "공원", "해수욕장", "해변"]):
        return "activity"
    return "other"


# ─── bucket 예비 분류 + activity 필터링 ───
# 음식점/카페는 항상 유지
# activity/other는 유저가 선택한 활동 키워드에 매칭되는 장소만 유지
def filter_by_bucket_and_activity(
        places: list[dict],
        activity_keywords: list[str],
) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        bucket = classify_bucket(p)
        # bucket 예비 분류 결과 저장
        p = {**p, "_bucket": bucket}

        # 음식점/카페는 항상 통과
        if bucket in ("food", "cafe"):
            filtered.append(p)
            continue

        # activity/other는 유저 선택 활동 키워드 매칭 시만 통과
        if not activity_keywords:
            filtered.append(p)
            continue

        name     = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in activity_keywords):
            filtered.append(p)

    return filtered, len(places) - len(filtered)


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


# ─── 여행과 무관한 키워드 제거 (category/name 분리) ───
def filter_by_irrelevant(places: list[dict]) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        name     = p.get("name", "") or ""
        category = p.get("category", "") or ""

        # category 기반 제거
        if any(kw in category for kw in EXCLUDE_KEYWORDS):
            continue
        # name 기반 제거
        if any(kw in name for kw in EXCLUDE_KEYWORDS_NAME):
            continue

        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── activities 선택 여부 기반 제거 (category에서만 매칭) ───
def filter_by_activity_exclude(
        places: list[dict],
        activities_kr: list[str],
) -> tuple[list[dict], int]:
    exclude_keywords = []
    for activity, rule in ACTIVITY_EXCLUDE_KEYWORDS.items():
        if activity not in activities_kr:
            exclude_keywords.extend(rule.get("exclude_if_not_selected", []))

    if not exclude_keywords:
        return places, 0

    filtered = []
    for p in places:
        category = p.get("category", "") or ""
        if any(kw in category for kw in exclude_keywords):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 세부 카테고리별 중복 제한 ───
def filter_by_subcategory_cap(
        places: list[dict],
        max_per_subcategory: int = 2,
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


# ─── 활동/동행자별 우선순위 정렬 ───
def boost_by_priority(
        places: list[dict],
        companion_kr: str,
        activities_kr: list[str],
) -> list[dict]:
    priority_keywords = []

    # 동행자 기반 우선순위 키워드
    if companion_kr in PRIORITY_KEYWORDS:
        kw_map = PRIORITY_KEYWORDS[companion_kr]
        priority_keywords.extend(kw_map.get("name", []))
        priority_keywords.extend(kw_map.get("category", []))

    # 술/바 선택 시 우선순위 키워드
    if "술/바" in activities_kr and "술/바" in PRIORITY_KEYWORDS:
        kw_map = PRIORITY_KEYWORDS["술/바"]
        priority_keywords.extend(kw_map.get("name", []))
        priority_keywords.extend(kw_map.get("category", []))

    if not priority_keywords:
        return places

    priority = []
    others   = []
    for p in places:
        name     = p.get("name", "") or ""
        category = p.get("category", "") or ""
        if any(kw in name or kw in category for kw in priority_keywords):
            priority.append(p)
        else:
            others.append(p)

    return priority + others


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

        if matched and not chain:  return 0
        if matched and chain:      return 1
        if not chain:              return 2
        return 3

    return sorted(places, key=priority)


# ─── cap 적용 ───
def filter_by_category_cap(
        places: list[dict],
        travel_days: int = 1,
        route_type: str = "endpoint",
) -> tuple[list[dict], int]:

    if route_type == "only":
        cap        = ONLY_FILTER_CAP.get(travel_days, ONLY_FILTER_CAP[1])
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
        code   = p.get("category_group_code", "")
        bucket = p.get("_bucket", "")

        # _bucket 기준으로 cafe/food 분류 (CE7이라도 activity면 others로)
        if bucket == "cafe" or (code == "CE7" and bucket != "activity"):
            if cafe_count >= cafe_cap:
                continue
            cafe_count += 1
        elif bucket == "food" or code == "FD6":
            if food_count >= food_cap:
                continue
            food_count += 1
        else:
            if others_count >= others_cap:
                continue
            others_count += 1

        filtered.append(p)

    return filtered, len(places) - len(filtered)