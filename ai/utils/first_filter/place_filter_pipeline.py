# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 1차 필터링 함수 모음
#
# 흐름:
#   1. 키워드 제거
#      - avoid_activities 제거
#      - 여행과 무관한 키워드 제거 (category: EXCLUDE_KEYWORDS, name: EXCLUDE_KEYWORDS_NAME)
#      - activities 선택 여부 기반 제거 (category: ACTIVITY_EXCLUDE_KEYWORDS)
#      - 세부 카테고리별 중복 제한 (동일 카테고리 최대 2개)
#   2. 경로 인접성 정렬 (endpoint 전용)
#      - start~end 직선 경로에서 수직 거리가 먼 장소를 뒤로 정렬
#   3. 정렬
#      - 활동/동행자별 장소 우선 정렬 (PRIORITY_KEYWORDS)
#      - final_keywords category 매칭 → 최우선
#      - name_search_keywords name 매칭 → 다음
#      - 프랜차이즈 → 뒤로
#   4. cap 적용
# ─────────────────────────────────────────────────────────────────────

import math
from constants.place_keywords import (
    EXCLUDE_KEYWORDS,
    EXCLUDE_KEYWORDS_NAME,
    ACTIVITY_EXCLUDE_KEYWORDS,
    KEYWORD_EXPANSIONS,
    PRIORITY_KEYWORDS,
)


# ─── Haversine ───
def _haversine(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ─── 점 → 직선(start-end) 수직 거리 ───
def _perpendicular_distance(lat, lng, start_lat, start_lng, end_lat, end_lng):
    def to_xy(la, ln):
        x = ln * math.cos(math.radians(start_lat))
        y = la
        return x, y

    px, py = to_xy(lat, lng)
    sx, sy = to_xy(start_lat, start_lng)
    ex, ey = to_xy(end_lat, end_lng)

    line_len_sq = (ex - sx) ** 2 + (ey - sy) ** 2
    if line_len_sq == 0:
        return _haversine(lat, lng, start_lat, start_lng)

    t = max(0, min(1, ((px - sx) * (ex - sx) + (py - sy) * (ey - sy)) / line_len_sq))
    closest_x = sx + t * (ex - sx)
    closest_y = sy + t * (ey - sy)
    closest_lat = closest_y
    closest_lng = closest_x / math.cos(math.radians(start_lat))
    return _haversine(lat, lng, closest_lat, closest_lng)


# ─── 경로 인접성 기준 정렬 (endpoint 전용) ───
# start~end 직선에서 수직거리가 가까운 장소를 우선 배치 (cap에서 살아남을 확률 ↑)
def sort_by_route_proximity(
    places:    list[dict],
    start_lat: float,
    start_lng: float,
    end_lat:   float,
    end_lng:   float,
) -> list[dict]:
    def distance_key(p):
        lat = p.get("lat")
        lng = p.get("lng")
        if lat is None or lng is None:
            return float("inf")
        return _perpendicular_distance(lat, lng, start_lat, start_lng, end_lat, end_lng)

    return sorted(places, key=distance_key)

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

# ─── only 케이스: K-means 분할 후 day당 cap (전체 cap ÷ travel_days 기준) ───
ONLY_DAY_FILTER_CAP = {
    1: {"total": 50, "CE7": 8, "FD6": 12, "others": 30},
    2: {"total": 40, "CE7": 6, "FD6": 9,  "others": 25},
    3: {"total": 33, "CE7": 5, "FD6": 8,  "others": 20},
    4: {"total": 30, "CE7": 5, "FD6": 7,  "others": 18},
}

# ─── 체험형 카페 키워드 (CE7이지만 activity로 분류) ───
ACTIVITY_CAFE_KEYWORDS = [
    "보드카페", "만화카페", "만화방", "방탈출", "방탈출카페",
    "애견카페", "고양이카페", "동물카페", "VR카페",
]

# ─── 디저트류 키워드 (FD6이지만 cafe로 분류) ───
# "앉아서 쉴 수 있는 디저트류"만 cafe로 — 닭강정·떡,한과 같은
# 테이크아웃 먹거리는 food 유지 (간식 전체를 넣으면 닭강정집이
# cafe cap을 잠식해 진짜 카페가 코스에서 사라지는 문제 발생)
CAFE_FOOD_KEYWORDS = ["제과", "베이커리", "디저트", "아이스크림", "도넛"]


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
# *(v3.1)* 힌트 앵커는 이 필터에서도 예외 — 이전까지 필터 4개(irrelevant/
# activity_exclude/subcategory_cap/여기)를 모두 고쳤다고 생각했는데, 이 함수만
# 유일하게 is_hint_anchor 보호가 아예 없어서 삼척중앙시장("가정,생활>시장" →
# bucket="other"), 삼척문화예술회관("문화,예술>...>공연장,연극극장" → bucket=
# "activity") 둘 다 유저가 해당 activity(예: 공연/문화)를 선택하지 않으면
# activity_keywords 매칭에 실패해 여기서 조용히 제거되고 있었음.
def filter_by_bucket_and_activity(
        places: list[dict],
        activity_keywords: list[str],
        hint_keywords: list[str] = None,
) -> tuple[list[dict], int]:
    hint_kws = hint_keywords or []
    filtered = []
    for p in places:
        bucket = classify_bucket(p)
        # bucket 예비 분류 결과 저장
        p = {**p, "_bucket": bucket}

        # 힌트 앵커(태그 또는 이름 fallback)는 무조건 통과
        if _is_hint_protected(p, hint_kws):
            filtered.append(p)
            continue

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


# ─── 힌트 보호 판정 (태그 + 이름 fallback) ───
# *(v3.1)* is_hint_anchor 태그가 정석 경로지만, 앵커 해석(_resolve_anchors)과
# 다른 place_id로 보충 수집(_collect_around_anchors 등)에 동일 장소의 "다른 카피"가
# 들어오면 그 카피에는 태그가 없다. 태그가 없어도 이름이 힌트 키워드와
# 일치하면 힌트로 간주 — 제거/cap 필터 쪽에도 적용해서 "힌트 장소가 사라지면
# 안 된다"를 보장한다.
# *(v3.1 재수정)* 부분 문자열 포함(in) 매칭은 "삼척항" 같은 짧고 흔한 힌트
# 키워드가 "컴포즈커피 삼척항점"/"메가MGC커피 삼척항점"처럼 이름에 그 지명이
# 우연히 들어간 무관한 가게까지 전부 힌트로 오인하게 만드는 문제가 있었음.
# 공백 제거 후 "완전 일치"만 힌트로 인정하도록 좁힘 — "도째비골 스카이밸리"
# (힌트) vs "도째비골스카이밸리"(카카오 상호) 같은 순수 띄어쓰기 차이만 흡수.
def _hint_name_matched(place: dict, hint_kws: list[str]) -> bool:
    if not hint_kws:
        return False
    name_n = (place.get("name", "") or "").replace(" ", "")
    if not name_n:
        return False
    return any(
        name_n == h.replace(" ", "")
        for h in hint_kws if h
    )


def _is_hint_protected(place: dict, hint_kws: list[str]) -> bool:
    return bool(place.get("is_hint_anchor")) or _hint_name_matched(place, hint_kws)


# ─── 여행과 무관한 키워드 제거 (category/name 분리) ───
def filter_by_irrelevant(
        places: list[dict],
        hint_keywords: list[str] = None,
) -> tuple[list[dict], int]:
    hint_kws = hint_keywords or []
    filtered = []
    for p in places:
        # *(v3.1)* 힌트 앵커는 이 필터에서 제외 — 삼척중앙시장("가정,생활 > 시장"),
        # 묵호항("교통,수송 > 교통시설 > 항구,포구")처럼 카카오 카테고리가
        # "여행"이 아닌 생활/교통 카테고리로 잡히는 실존 명소·앵커가
        # EXCLUDE_KEYWORDS("시장", "교통", "수송" 등)에 걸려 통째로 제거되는 문제가 있었음
        # 태그가 없는 보충 수집 카피도 이름 매칭으로 함께 보호
        if _is_hint_protected(p, hint_kws):
            filtered.append(p)
            continue

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
        hint_keywords: list[str] = None,
) -> tuple[list[dict], int]:
    hint_kws = hint_keywords or []
    exclude_keywords = []
    for activity, rule in ACTIVITY_EXCLUDE_KEYWORDS.items():
        if activity not in activities_kr:
            exclude_keywords.extend(rule.get("exclude_if_not_selected", []))

    if not exclude_keywords:
        return places, 0

    filtered = []
    for p in places:
        # *(v3.1)* 힌트 앵커는 이 필터에서도 제외 — 같은 이유 (+ 이름 fallback)
        if _is_hint_protected(p, hint_kws):
            filtered.append(p)
            continue

        category = p.get("category", "") or ""
        if any(kw in category for kw in exclude_keywords):
            continue
        filtered.append(p)

    return filtered, len(places) - len(filtered)


# ─── 세부 카테고리별 중복 제한 ───
# *(v3.1)* 힌트 앵커는 이 cap에서 제외. 카카오 카테고리가 "여행 > 관광,명소"처럼
# 두루뭉술한 값이라, 논골담길·도째비골스카이밸리 같은 완전히 다른 실존 핫플이
# 같은 서브카테고리로 묶여 cap에 걸려 통째로 잘리는 문제가 있었음
# (앵커가 아닌 일반 명소는 여전히 cap 적용 — 잡다한 동상·기념비 난립 방지)
# 태그가 없는 보충 수집 카피도 이름 매칭으로 함께 보호 (fallback)
# *(v3.1 재수정)* max_per_subcategory 2 → 3. 이 cap은 아직 블로그 리뷰 기반
# 품질 점수(second_filter)를 모르는 시점에 카카오 API 반환 순서만으로 컷하기
# 때문에, 2개로는 "그린회관/부명손칼국수/바다내음"처럼 같은 세부카테고리에
# 진짜 맛집이 여럿 있는 경우 순서상 밀려서 second_filter의 품질 평가 기회조차
# 못 받고 잘리는 문제가 있었음. day 단위 카테고리 총량 cap(DAY_CATEGORY_CAP 등)이
# 하위 안전망으로 여전히 있어 3으로 늘려도 특정 카테고리가 폭주하진 않음.
def filter_by_subcategory_cap(
        places: list[dict],
        max_per_subcategory: int = 3,
        hint_keywords: list[str] = None,
) -> tuple[list[dict], int]:
    hint_kws = hint_keywords or []
    subcategory_count = {}
    filtered = []

    for p in places:
        if _is_hint_protected(p, hint_kws):
            filtered.append(p)
            continue

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
# -1: 힌트 앵커(is_hint_anchor 태그) 또는 힌트 장소명 매칭 (v3.1 — cap에서 살아남도록 최우선 배치)
# 0: final_keywords category 매칭 + 비프랜차이즈
# 1: name_search_keywords name 매칭 + 비프랜차이즈
# 2: final_keywords category 매칭 + 프랜차이즈
# 3: name_search_keywords name 매칭 + 프랜차이즈
# 4: 나머지 비프랜차이즈
# 5: 나머지 프랜차이즈
# ───
def sort_by_priority(
        places: list[dict],
        final_keywords: list[str] = None,
        name_search_keywords: list[str] = None,
        hint_keywords: list[str] = None,
) -> list[dict]:
    final_kws = final_keywords or []
    name_kws  = name_search_keywords or []
    hint_kws  = hint_keywords or []

    def priority(p):
        name     = p.get("name", "") or ""
        category = p.get("category", "") or ""
        chain    = is_chain_brand(p)

        # 힌트 앵커(태그 또는 이름 완전 일치 fallback)는 무조건 최우선 *(v3.1)*
        # (공백 제거 후 비교 — "도째비골 스카이밸리" vs "도째비골스카이밸리")
        # *(v3.1 재수정)* 부분 문자열 포함 매칭은 "삼척항" 같은 짧은 힌트가
        # 무관한 상호(예: 메가MGC커피 삼척항점)까지 매칭시키는 문제가 있어 완전 일치로 좁힘
        if _is_hint_protected(p, hint_kws):
            return -1

        category_matched = bool(final_kws) and any(kw in category for kw in final_kws)
        name_matched     = bool(name_kws) and any(kw in name for kw in name_kws)

        if category_matched and not chain: return 0
        if name_matched and not chain:     return 1
        if category_matched and chain:     return 2
        if name_matched and chain:         return 3
        if not chain:                      return 4
        return 5

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
    elif route_type == "only_day":
        cap        = ONLY_DAY_FILTER_CAP.get(travel_days, ONLY_DAY_FILTER_CAP[1])
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