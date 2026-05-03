# ─────────────────────────────────────────────────────────────────────
# validate_input
# ─────────────────────────────────────────────────────────────────────
# 사용자 입력 검증 + 전처리 노드
#
# 흐름:
#   1. 필수 필드 검증
#   2. 위치 → 좌표 변환 - 실패 시 SEOUL_CENTER fallback (geocode_kakao 호출)
#   3. 식사 시간 계산 - needs_meal, meal_times
#   4. 검색 키워드 보강
#       - 필수 키워드 추가 (맛집, 카페)
#       - 분위기/일행 기반 관련 활동 추가 (expand_by_context 호출)
# ─────────────────────────────────────────────────────────────────────

from utils.geocode import geocode_kakao
from utils.expand_by_context import expand_by_context
from constants.location import DEFAULT_RADIUS_KM, SEOUL_CENTER

def validate_input(state: dict) -> dict:

    ui = dict(state["user_input"])
    errors = []
    warnings = []

    # 필수 필드 체크
    required_fields = [
        "location", "party_size", "party_type",
        "start_time", "end_time", "total_hours",
        "mood_preferences", "activity_preferences",
    ]

    for field in required_fields:
        if ui.get(field) is None or ui.get(field) == "":
            errors.append(f"필수 필드 누락: {field}")

    if ui.get("party_size", 0) <= 0:
        errors.append("party_size는 1 이상이어야 합니다")

    if not ui.get("mood_preferences"):
        warnings.append("분위기 선호가 비어있어 기본값 적용")

    if not ui.get("activity_preferences"):
        warnings.append("활동 선호가 비어있어 기본값 적용")

    # 위치 → 좌표 변환
    loc = ui.get("location", "") or ""
    coords, err = geocode_kakao(loc) if loc else (None, "location 비어 있음")

    if coords:
        ui["center_lat"], ui["center_lng"] = coords
        ui["search_radius_km"] = DEFAULT_RADIUS_KM
    else:
        ui["center_lat"], ui["center_lng"] = SEOUL_CENTER
        ui["search_radius_km"] = 2.0
        warnings.append(f"fallback 사용: {err}")

    # 식사 시간 계산
    def to_hour(t: str) -> float:
        h, m = t.split(":")
        return int(h) + int(m) / 60

    start_h = to_hour(ui["start_time"])
    end_h = to_hour(ui["end_time"])

    meal_times = []

    if start_h <= 12.0 and end_h >= 13.0:
        meal_times.append("12:30")

    if start_h <= 18.0 and end_h >= 19.0:
        meal_times.append("18:30")

    ui["meal_times"] = meal_times
    ui["needs_meal"] = len(meal_times) > 0

    if not ui["needs_meal"]:
        warnings.append("식사 시간 없음 → 식당 추천 생략")

    # ── 필수 키워드 추가 ──
    activity_prefs = list(ui.get("activity_preferences") or [])
    mood_prefs = ui.get("mood_preferences") or []
    party_type = ui.get("party_type", "")

    # 분위기/일행 기반 활동 키워드 보강
    final_keywords = expand_by_context(
        activity_preferences=activity_prefs,
        mood_preferences=mood_prefs,
        party_type=party_type,
        target_count=5,
    )

    # 맛집: 식사 필요할 때 맛집 추가
    if ui.get("needs_meal") and "맛집" not in final_keywords:
        final_keywords.append("맛집")

    # 카페: 긴 코스 + 힐링 무드일 때 카페 보강 ( 이미 있으면 skip)
    if (
            ui.get("total_hours", 0) >= 4
            and "힐링" in (ui.get("mood_preferences") or [])
            and "카페" not in final_keywords
    ):
        final_keywords.append("카페")

    ui["final_keywords"] = final_keywords

    return {
        "user_input": ui,
        "errors": errors,
        "warnings": warnings,
        "step": "validated",
    }