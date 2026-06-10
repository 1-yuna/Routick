# ─────────────────────────────────────────────────────────────────────
# preprocess_input
# ─────────────────────────────────────────────────────────────────────
# 전처리 노드
#
# 흐름:
#   1. 변수값 매핑 (camelCase → snake_case, 영어 → 한국어)
#   2. 좌표 설정
#   3. 키워드 및 반경 설정 (set_keyword_radius)
# ─────────────────────────────────────────────────────────────────────


from constants.mapping import (
    TRAVEL_DAYS_MAP,
    COMPANION_MAP,
    AGE_GROUP_MAP,
    TRANSPORT_MAP,
    MOODS_MAP,
    ACTIVITIES_MAP,
    RADIUS_MAP,
)

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

    # ─── 4. 키워드 설정 (set_keyword_radius) ───
    final_keywords = list(ui.get("activities_kr") or [])

    # 맛집 무조건 포함 (항상 맨 앞에)
    if "맛집" not in final_keywords:
        final_keywords.insert(0, "맛집")

    # 카페 무조건 포함
    if "카페" not in final_keywords:
        final_keywords.insert(1, "카페")

    # 당일치기 제외 숙소 포함
    if travel_days > 1 and "숙박" not in final_keywords:
        final_keywords.append("숙박")

    ui["final_keywords"] = final_keywords

    return {
        "user_input": ui,
        "warnings": warnings,
        "step": "preprocessed",
    }