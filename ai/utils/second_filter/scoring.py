# ─────────────────────────────────────────────────────────────────────
# utils/scoring.py
# ─────────────────────────────────────────────────────────────────────
# 분위기 점수 계산
#
# 흐름:
#   1. 분위기 점수 계산 ( 사용자 - mood_preferences, 장소 - atmosphere)
#   3. 구성원 적합도 점수 (구성원, 인원수, 연령대)
# ─────────────────────────────────────────────────────────────────────

from constants.scoring import (PARTY_SIZE_PENALTY, AGE_PENALTY, REVISIT_SCORE_MAP)

# ─── 분위기 점수 계산 ───
def calc_mood_score(place: dict, mood_preferences: list[str]) -> int:
    atmosphere = place.get("atmosphere", [])
    # 데이터 없으면 점수 없음
    if not atmosphere or not mood_preferences:
        return 0

    # 사용자가 원하는 분위기 중 몇 개가 매칭되는지 계산
    return sum(10 for m in mood_preferences if m in atmosphere)


#  ─── 활동 점수 계산 ───
def calc_activity_score(place, activity_preferences):
    place_tags = set(place.get("place_tags", []))

    if not place_tags or not activity_preferences:
        return 0

    score = 0

    for a in activity_preferences:
        if a in place_tags:
            score += 10   # 핵심 매칭

    return score



# ─── 구성원 적합도 점수 ───
def calc_party_fit_score(
        place: dict,
        party_type: str,
        party_size: int,
        age_group: str,
) -> int:
    best_for = place.get("best_for", [])
    category = place.get("category", "")
    name = place.get("name", "")

    score = 0

    # party_type 매칭
    # 구성원 유형이 포함되어 있으면 +1
    if best_for and party_type in best_for:
        score += 20

    # party_size 적합 여부
    # 1인 - 단체/대형 장소 부적합, 5인 이상: 협소한 공간은 부적합
    penalty_keywords = PARTY_SIZE_PENALTY.get(party_size, [])
    if not any(kw in category or kw in name for kw in penalty_keywords):
        score += 10   # 패널티 없으면 +1

    # 연령대 적합 여부
    # 연령대별로 부적합한 장소 키워드들 제외
    age_penalties = AGE_PENALTY.get(age_group, [])
    if not any(kw in category or kw in name for kw in age_penalties):
        score += 10   # 문제 없으면 +1

    return score


# 재방문 의사
def calc_revisit_score(place: dict) -> int:
    intent = place.get("revisit_intent", "low")
    return REVISIT_SCORE_MAP.get(intent, 0)

# 최종 종합 점수
def calc_total_score(
        mood_score: int,
        activity_score: int,
        party_fit_score: int,
        revisit_score: int,
) -> int:

    score = 0

    # 감성 요소
    score += mood_score

    # 구성 적합도
    score += party_fit_score

    # 활동 적합
    score += activity_score

    # 재방문 의사
    score += revisit_score

    return score