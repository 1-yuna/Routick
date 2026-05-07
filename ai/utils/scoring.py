# utils/scoring.py

from constants.scoring import (PARTY_SIZE_PENALTY, AGE_PENALTY)


def calc_mood_score(place: dict, mood_preferences: list[str]) -> float:
    atmosphere = place.get("atmosphere", [])
    if not atmosphere or not mood_preferences:
        return 0.0

    matched = sum(1 for m in mood_preferences if m in atmosphere)
    return matched / len(mood_preferences)


def calc_activity_score(place: dict, activity_preferences: list[str]) -> float:
    category = place.get("category", "")
    name = place.get("name", "")
    if not activity_preferences:
        return 0.0

    matched = sum(1 for a in activity_preferences if a in category or a in name)
    return matched / len(activity_preferences)


def calc_party_fit_score(
        place: dict,
        party_type: str,
        party_size: int,
        age_group: str,
) -> float:
    best_for = place.get("best_for", [])
    category = place.get("category", "")
    name = place.get("name", "")
    score = 1.0

    # ─── party_type 매칭 ───
    if best_for and party_type not in best_for:
        score -= 0.3

    # ─── party_size 패널티 ───
    penalty_keywords = PARTY_SIZE_PENALTY.get(party_size, [])
    if any(kw in category or kw in name for kw in penalty_keywords):
        score -= 0.4

    # ─── 연령대 패널티 ───
    age_penalties = AGE_PENALTY.get(age_group, [])
    if any(kw in category or kw in name for kw in age_penalties):
        score -= 0.5

    return max(score, 0.0)


def calc_total_score(
        mood_score: float,
        activity_score: float,
        party_fit_score: float,
        party_type: str,
        activity_preferences: list[str],
) -> float:
    # 기본 가중치
    mood_w = 0.4
    activity_w = 0.4
    party_w = 0.2

    # 연인이면 mood 가중치 ↑
    if party_type == "연인":
        mood_w = 0.5
        activity_w = 0.3
        party_w = 0.2

    # 활동 선호 명확하면 activity 가중치 ↑
    if len(activity_preferences) >= 4:
        activity_w += 0.1
        mood_w -= 0.1

    return round(
        mood_score * mood_w +
        activity_score * activity_w +
        party_fit_score * party_w,
        4
    )