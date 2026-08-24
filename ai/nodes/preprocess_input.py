# ─────────────────────────────────────────────────────────────────────
# preprocess_input
# ─────────────────────────────────────────────────────────────────────
# 전처리 노드
#
# 입력 계약: Spring이 snake_case로 전달 (route_type, start_lat, ...)
#
# 흐름:
#   1. 전처리
#      - 영어 값 → 한국어 값 변환
#      - travel_date → 요일 변환 (영업시간 체크용)
#      - 여행 시간 미입력 시 기본값 적용
#   2. 키워드 설정 및 확장
#      - activities에 음식점, 카페 무조건 추가
#      - 자녀일 경우 키즈카페, 놀이교육 추가
#      - KEYWORD_EXPANSIONS 기반 동의어 확장 → final_keywords
#      - NAME_SEARCH_KEYWORDS 기반 name 검색 전용 키워드 추출 → name_search_keywords
# ─────────────────────────────────────────────────────────────────────

from datetime import datetime

from constants.mapping import (
    TRAVEL_DAYS_MAP,
    COMPANION_MAP,
    TRANSPORT_MAP,
    MOODS_MAP,
    ACTIVITIES_MAP,
    WEEKDAY_MAP,
    DEFAULT_START_TIME,
    DEFAULT_END_TIME,
)
from constants.place_keywords import KEYWORD_EXPANSIONS, NAME_SEARCH_KEYWORDS


# ─── 키워드 동의어 확장 ───
def expand_keywords(keywords: list[str]) -> list[str]:
    expanded = []
    seen = set()
    for kw in keywords:
        for ex in KEYWORD_EXPANSIONS.get(kw, [kw]):
            if ex not in seen:
                seen.add(ex)
                expanded.append(ex)
    return expanded


# ─── [노드] 전처리 ───
def preprocess_input(state: dict) -> dict:
    ui = dict(state["user_input"])
    warnings = []

    # ── 1. 전처리 ────────────────────────────────────────────────────
    travel_days = ui.get("travel_days", 1)
    companion   = ui.get("companion", "")
    transport   = ui.get("transport", "walk")
    moods       = ui.get("moods") or []
    activities  = ui.get("activities") or []

    ui["companion_kr"]  = COMPANION_MAP.get(companion, companion)
    ui["transport_kr"]  = TRANSPORT_MAP.get(transport, transport)
    ui["duration_kr"]   = TRAVEL_DAYS_MAP.get(travel_days, "당일")
    ui["moods_kr"]      = [MOODS_MAP.get(m, m) for m in moods]
    ui["activities_kr"] = [ACTIVITIES_MAP.get(a, a) for a in activities]

    travel_date = ui.get("travel_date", "")
    if travel_date:
        try:
            dt = datetime.strptime(travel_date, "%Y-%m-%d")
            ui["travel_weekday"] = WEEKDAY_MAP[dt.weekday()]
        except ValueError:
            warnings.append(f"travel_date 파싱 실패: {travel_date}")
            ui["travel_weekday"] = None
    else:
        warnings.append("travel_date 없음 → travel_weekday None")
        ui["travel_weekday"] = None

    if not ui.get("start_time"):
        warnings.append(f"start_time 없음 → 기본값 {DEFAULT_START_TIME} 적용")
        ui["start_time"] = DEFAULT_START_TIME
    if not ui.get("end_time"):
        warnings.append(f"end_time 없음 → 기본값 {DEFAULT_END_TIME} 적용")
        ui["end_time"] = DEFAULT_END_TIME

    # ── 2. 키워드 설정 및 확장 ──────────────────────────────────────
    base_keywords = list(ui["activities_kr"])

    # 음식점, 카페 무조건 추가
    if "음식점" not in base_keywords:
        base_keywords.insert(0, "음식점")
    if "카페" not in base_keywords:
        base_keywords.insert(1, "카페")

    # 자녀와일 경우 키즈카페, 놀이교육 자동 추가
    if companion == "children":
        for kw in ["키즈카페", "놀이교육"]:
            if kw not in base_keywords:
                base_keywords.append(kw)

    ui["final_keywords"] = expand_keywords(base_keywords)

    name_keywords = []
    seen = set()
    for activity_kr in ui["activities_kr"]:
        for kw in NAME_SEARCH_KEYWORDS.get(activity_kr, []):
            if kw not in seen:
                seen.add(kw)
                name_keywords.append(kw)
    ui["name_search_keywords"] = name_keywords

    route_type = ui.get("route_type", "only")
    if route_type == "only":
        if ui.get("lat") is None or ui.get("lng") is None:
            warnings.append("route_type=only인데 lat/lng 없음")
    elif route_type == "endpoint":
        if not ui.get("days"):
            warnings.append("route_type=endpoint인데 days 없음")
    else:
        warnings.append(f"알 수 없는 route_type: {route_type}")

    return {
        "user_input": ui,
        "warnings":   warnings,
        "step":       "preprocessed",
    }