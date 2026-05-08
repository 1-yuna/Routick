# ─────────────────────────────────────────────────────────────────────
# validate_input
# ─────────────────────────────────────────────────────────────────────
# 사용자 입력 검증 + 전처리 노드
#
# 흐름:
#   1. 필수 필드 검증
#   2. 위치 → 좌표 변환 (geocode_kakao 호출)
#   3. 구성원 -> 검색 키워드 보강 (expand_by_context 호출)
# ─────────────────────────────────────────────────────────────────────

from utils.input.geocode import geocode_kakao
from utils.input.expand_activities_by_party import expand_activities_by_party
from constants.location import DEFAULT_RADIUS_KM, SEOUL_CENTER


# ─── [노드] 사용자 입력 검증 + 전처리 ───
def validate_input(state: dict) -> dict:

    ui = dict(state["user_input"])
    errors = []
    warnings = []

    # 필수 필드 체크
    required_fields = [
        "location", "party_size", "party_type",
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

    # 위치 → 좌표 변환 (geocode_kakao)
    loc = ui.get("location", "") or ""
    coords, err = geocode_kakao(loc) if loc else (None, "location 비어 있음")

    # 성공 시
    if coords:
        ui["center_lat"], ui["center_lng"] = coords
        ui["search_radius_km"] = DEFAULT_RADIUS_KM
    # 실패 시
    else:
        ui["center_lat"], ui["center_lng"] = SEOUL_CENTER
        ui["search_radius_km"] = 2.0
        warnings.append(f"fallback 사용: {err}")

    # 구성원 -> 활동 키워드 보강 (expand_by_context)
    activity_prefs = list(ui.get("activity_preferences") or [])
    party_type = ui.get("party_type", "")

    final_keywords = expand_activities_by_party(
        activity_preferences=activity_prefs,
        party_type=party_type,
        target_count=5,
    )

    # 카페: 긴 코스 + 힐링 무드일 때 카페 보강 - 이미 있으면 skip
    if ( ui.get("total_hours", 0) >= 4
        and "힐링" in (ui.get("mood_preferences") or [])
        and "카페" not in final_keywords ):
        final_keywords.append("카페")

    ui["final_keywords"] = final_keywords

    return {
        "user_input": ui,
        "errors": errors,
        "warnings": warnings,
        "step": "validated",
    }