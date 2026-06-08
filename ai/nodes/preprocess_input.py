# ─────────────────────────────────────────────────────────────────────
# preprocess_input
# ─────────────────────────────────────────────────────────────────────
# 전처리 노드
#
# 흐름:
#   1. 변수값 매핑 (camelCase → snake_case, 영어 → 한국어)
#   2. 키워드 및 반경 설정 (set_keyword_radius)
# ─────────────────────────────────────────────────────────────────────

from utils.input.expand_activities_by_party import expand_activities_by_party

# ─── 매핑 테이블 ───
TRAVEL_DAYS_MAP = {
    1: "당일",
    2: "1박2일",
    3: "2박3일",
    4: "3박4일",
}

COMPANION_MAP = {
    "solo":     "혼자",
    "couple":   "연인",
    "friend":   "친구",
    "parents":  "부모님과",
    "children": "자녀와",
    "pet":      "반려동물과",
}

AGE_GROUP_MAP = {
    "10s":   "10대",
    "20s":   "20대",
    "30s":   "30대",
    "40s":   "40대",
    "50plus": "50대",
}

TRANSPORT_MAP = {
    "walk": "도보",
    "car":  "자동차",
}

MOODS_MAP = {
    "active":       "활기찬",
    "healing":      "힐링",
    "sensibility":  "감성",
    "quiet":        "조용한",
    "warm":         "따뜻한",
    "romantic":     "로맨틱",
    "clean":        "깔끔한",
    "vintage":      "빈티지",
    "hip":          "힙한",
}

ACTIVITIES_MAP = {
    "tour/exhibition":      "관광/전시",
    "performance/culture":  "공연/문화",
    "thrill/experience":    "스릴/체험",
    "entertainment/sports": "오락/스포츠",
    "nature/walk":          "자연/산책",
    "shopping":             "쇼핑",
    "indoor":               "실내오락",
    "bar":                  "술/바",
}

# ─── 이동수단/여행기간 기반 검색 반경 (km) ───
RADIUS_MAP = {
    "walk": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    "car":  {1: 5.0, 2: 8.0, 3: 10.0, 4: 12.0},
}


# ─── [노드] 전처리 ───
def preprocess_input(state: dict) -> dict:
    ui = dict(state["user_input"])
    warnings = []

    # ─── 1. 변수값 매핑 ───
    travel_days = ui.get("travel_days", 1)
    companion = ui.get("companion", "")
    age_group = ui.get("age_group", "")
    transport = ui.get("transport", "walk")
    moods = ui.get("moods") or []
    activities = ui.get("activities") or []

    ui["companion_kr"] = COMPANION_MAP.get(companion, companion)
    ui["age_group_kr"] = AGE_GROUP_MAP.get(age_group, age_group)
    ui["transport_kr"] = TRANSPORT_MAP.get(transport, transport)
    ui["duration_kr"] = TRAVEL_DAYS_MAP.get(travel_days, "당일")
    ui["moods_kr"] = [MOODS_MAP.get(m, m) for m in moods]
    ui["activities_kr"] = [ACTIVITIES_MAP.get(a, a) for a in activities]

    # ─── 2. 좌표 설정 ───
    ui["center_lat"] = ui.get("lat")
    ui["center_lng"] = ui.get("lng")

    # ─── 3. 검색 반경 설정 (set_keyword_radius) ───
    radius_by_transport = RADIUS_MAP.get(transport, RADIUS_MAP["walk"])
    ui["search_radius_km"] = radius_by_transport.get(travel_days, 1.0)

    # ─── 4. 키워드 보강 (set_keyword_radius) ───
    final_keywords = expand_activities_by_party(
        activity_preferences=list(ui.get("activities_kr") or []),
        companion=ui.get("companion_kr", ""),
        target_count=5,
    )

    # 맛집 무조건 포함 (항상 맨 앞에)
    if "맛집" not in final_keywords:
        final_keywords.insert(0, "맛집")

    # 카페 보강: 힐링 무드 + 긴 코스일 때
    if (
        travel_days >= 2
        and "힐링" in ui.get("moods_kr", [])
        and "카페" not in final_keywords
    ):
        final_keywords.append("카페")
        warnings.append("힐링 무드 + 장기 여행 → 카페 키워드 자동 추가")

    ui["final_keywords"] = final_keywords

    return {
        "user_input": ui,
        "warnings": warnings,
        "step": "preprocessed",
    }