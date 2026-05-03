# utils/keyword_expansion.py
# ─────────────────────────────────────────────────────────────────────
# 사용자 컨텍스트(분위기/일행) 기반 활동 키워드 보강
#
# 동작:
#   - 사용자 activity_preferences 가 적을 때, 분위기/일행 정보 참고해서
#     관련된 활동 키워드를 자동 추가
#   - 활동 충분히 골랐으면 그대로 (사용자 의도 존중)
#
# 사용처:
#   - nodes/validate_input.py 에서 호출 → final_keywords 채움
# ─────────────────────────────────────────────────────────────────────

from constants.keywords import MOOD_TO_ACTIVITIES, PARTY_TO_ACTIVITIES


def expand_by_context(
    activity_preferences: list[str],
    mood_preferences: list[str],
    party_type: str,
    target_count: int = 5,
) -> list[str]:
    """
    분위기/일행 기반 활동 키워드 보강.

    Args:
        activity_preferences: 사용자가 직접 고른 활동 (예: ["카페", "보드게임카페"])
        mood_preferences:     사용자가 고른 분위기 (예: ["활기찬", "힐링"])
        party_type:           일행 유형 (예: "연인", "친구")
        target_count:         최종 목표 키워드 수 (기본 5개)

    Returns:
        보강된 활동 키워드 리스트 (중복 제거됨)

    Logic:
        1. 사용자 선택이 target_count 이상이면 그대로 (의도 명확)
        2. 미만이면 mood → party 순으로 채움
        3. target_count 도달하면 즉시 종료

    Example:
        activity_preferences=["카페", "보드게임카페"]
        mood_preferences=["활기찬"]
        party_type="친구"
        →
        ["카페", "보드게임카페", "pc방", "오락실", "노래방"]
    """
    expanded = list(activity_preferences)
    seen = set(expanded)

    # 이미 충분히 골랐으면 보강 안 함
    if len(expanded) >= target_count:
        return expanded

    # 1) 분위기 기반 보강
    for mood in mood_preferences:
        for activity in MOOD_TO_ACTIVITIES.get(mood, []):
            if activity not in seen:
                expanded.append(activity)
                seen.add(activity)
                if len(expanded) >= target_count:
                    return expanded

    # 2) 일행 유형 기반 보강
    for activity in PARTY_TO_ACTIVITIES.get(party_type, []):
        if activity not in seen:
            expanded.append(activity)
            seen.add(activity)
            if len(expanded) >= target_count:
                return expanded

    return expanded