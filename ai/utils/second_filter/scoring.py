# ─────────────────────────────────────────────────────────────────────
# scoring
# ─────────────────────────────────────────────────────────────────────
# 점수 계산
#
# 흐름:
#   1. mood_score    → 분위기 매칭 비율 기반 (최대 100점)
#   2. activity_score → 활동 매칭 비율 기반 (최대 100점)
#   3. party_fit_score → best_for에 companion 포함 시 (최대 40점)
#   4. revisit_score  → 재방문 의사 (최대 30점)
# ─────────────────────────────────────────────────────────────────────

REVISIT_SCORE_MAP = {
    "high":   30,
    "medium": 15,
    "low":    0,
}

# ─── best_for fallback (LLM 실패 시 카테고리 기반 기본값) ───
BEST_FOR_FALLBACK = {
    "CE7": ["연인", "친구", "혼자"],        # 카페
    "FD6": ["연인", "친구", "가족", "혼자"], # 음식점
    "AT4": ["연인", "친구", "가족"],         # 관광명소
    "AD5": ["연인", "친구", "가족"],         # 숙박
    "CT1": ["연인", "친구", "가족"],         # 문화시설
}


# ─── 분위기 점수 (비율 기반) ───
def calc_mood_score(place: dict, moods_kr: list[str]) -> float:
    atmosphere = place.get("atmosphere", [])
    if not atmosphere or not moods_kr:
        return 0

    matched = sum(1 for m in moods_kr if m in atmosphere)
    return round((matched / len(moods_kr)) * 100, 1)


# ─── 활동 점수 (비율 기반) ───
def calc_activity_score(place: dict, activities_kr: list[str]) -> float:
    place_tags = set(place.get("place_tags", []))
    if not place_tags or not activities_kr:
        return 0

    matched = sum(1 for a in activities_kr if a in place_tags)
    return round((matched / len(activities_kr)) * 100, 1)


# ─── 구성원 적합도 점수 ───
def calc_party_fit_score(place: dict, companion_kr: str) -> int:
    best_for = place.get("best_for", [])
    code = place.get("category_group_code", "")

    # best_for 비어있으면 fallback 적용
    if not best_for:
        best_for = BEST_FOR_FALLBACK.get(code, ["연인", "친구", "가족", "혼자"])

    # companion_kr을 best_for 비교용 키워드로 변환
    companion_map = {
        "혼자": "혼자",
        "연인": "연인",
        "친구": "친구",
        "부모님과": "부모님과",
        "자녀와": "자녀와",
        "반려동물과": "반려동물과",
    }
    companion_key = companion_map.get(companion_kr, companion_kr)

    return 40 if companion_key in best_for else 0


# ─── 재방문 의사 점수 ───
def calc_revisit_score(place: dict) -> int:
    intent = place.get("revisit_intent", "low")
    return REVISIT_SCORE_MAP.get(intent, 0)


# ─── 종합 점수 ───
def calc_total_score(
        mood_score: float,
        activity_score: float,
        party_fit_score: int,
        revisit_score: int,
) -> float:
    return mood_score + activity_score + party_fit_score + revisit_score