# ─────────────────────────────────────────────────────────────────────
# expand_by_context
# ─────────────────────────────────────────────────────────────────────
# 구성원 기반 활동 키워드 보강 -> 많은 pool 받기 위해
#
# 흐름:
#   1. 사용자 activity_preferences가 5개 미만일 떄 일행 정보 참고해서
#     관련된 활동 키워드를 자동 추가
#
# ─────────────────────────────────────────────────────────────────────

from constants.keywords import PARTY_TO_ACTIVITIES


# ─── 구성원 기반 활동 키워드 보강 ───
def expand_activities_by_party(
    activity_preferences: list[str],
    party_type: str,
    target_count: int = 5,
) -> list[str]:

    expanded = list(activity_preferences)
    seen = set(expanded)

    # 이미 충분히 골랐으면 보강 안 함
    if len(expanded) >= target_count:
        return expanded

    # 일행 유형 기반 보강
    for activity in PARTY_TO_ACTIVITIES.get(party_type, []):
        if activity not in seen:
            expanded.append(activity)
            seen.add(activity)
            if len(expanded) >= target_count:
                return expanded

    return expanded