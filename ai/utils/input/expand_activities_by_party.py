# ─────────────────────────────────────────────────────────────────────
# expand_activities_by_party (set_keyword_radius 내부에서 호출)
# ─────────────────────────────────────────────────────────────────────
# 동행 유형 기반 활동 키워드 보강
#
# 흐름:
#   1. activities 5개 미만일 때
#      동행 유형 기반으로 관련 키워드 자동 추가
# ─────────────────────────────────────────────────────────────────────

from constants.keywords import COMPANION_TO_ACTIVITIES

# ─── 동행 유형 기반 활동 키워드 보강 ───
def expand_activities_by_party(
    activity_preferences: list[str],
    companion: str,
    target_count: int = 5,
) -> list[str]:

    expanded = list(activity_preferences)
    seen = set(expanded)

    # 이미 충분히 골랐으면 보강 안 함
    if len(expanded) >= target_count:
        return expanded

    # 동행 유형 기반 보강
    for activity in COMPANION_TO_ACTIVITIES.get(companion, []):
        if activity not in seen:
            expanded.append(activity)
            seen.add(activity)
            if len(expanded) >= target_count:
                return expanded

    return expanded