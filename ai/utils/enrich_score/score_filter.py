# ─────────────────────────────────────────────────────────────────────
# score_filter
# ─────────────────────────────────────────────────────────────────────
# 점수 계산 (100점: 분위기30 + 활동30 + 동행자20 + 재방문의사20)
# + 2차 필터링 (하루 당 20개: 음식점7 / 카페3 / 활동관광10, 점수 순으로만 판단)
# ─────────────────────────────────────────────────────────────────────

DAY_SHORTLIST_QUOTA = {"food": 7, "cafe": 3, "activity": 10}

REVISIT_SCORE_MAP = {"high": 20, "medium": 10, "low": 0}

# ─── 동행자 매칭 기본값 (카테고리 기반, GPT 판단 없음) ───
BEST_FOR_FALLBACK = {
    "CE7": ["연인", "친구", "혼자", "부모님과"],
    "FD6": ["연인", "친구", "혼자", "부모님과", "자녀와"],
    "AT4": ["연인", "친구", "부모님과", "자녀와"],
    "CT1": ["연인", "친구", "부모님과"],
}
BEST_FOR_DEFAULT = ["연인", "친구", "혼자", "부모님과", "자녀와", "반려동물과"]


# ─── 분위기 점수 (매칭 비율 기반, 최대 30점) ───
def _score_mood(atmosphere: list[str], moods_kr: list[str]) -> float:
    if not atmosphere or not moods_kr:
        return 0
    matched = sum(1 for m in moods_kr if m in atmosphere)
    return round((matched / len(moods_kr)) * 30, 1)


# ─── 활동 점수 (사용자 선호 활동 매칭 개수 기반, 최대 30점) ───
def _score_activity(matched_activities: list[str]) -> int:
    count = len(matched_activities)
    if count >= 2:
        return 30
    if count == 1:
        return 15
    return 0


# ─── 동행자 점수 (카테고리 기반 기본값 매칭, 최대 20점) ───
def _score_party(category_group_code: str, companion_kr: str) -> int:
    best_for = BEST_FOR_FALLBACK.get(category_group_code, BEST_FOR_DEFAULT)
    return 20 if companion_kr in best_for else 0


# ─── 재방문의사 점수 (최대 20점) ───
def _score_revisit(revisit_intent: str) -> int:
    return REVISIT_SCORE_MAP.get(revisit_intent, 0)


# ─── 장소 하나에 LLM 보강 결과 머지 + 점수 계산 ───
def _merge_and_score(place: dict, enrich: dict, moods_kr: list[str], companion_kr: str) -> dict:
    atmosphere         = enrich.get("atmosphere", [])
    matched_activities = enrich.get("matched_activities", [])
    revisit_intent      = enrich.get("revisit_intent", "low")
    revisit_reason      = enrich.get("revisit_reason", "")
    summary              = enrich.get("summary", "")

    mood_score     = _score_mood(atmosphere, moods_kr)
    activity_score = _score_activity(matched_activities)
    party_fit_score = _score_party(place.get("category_group_code", ""), companion_kr)
    revisit_score  = _score_revisit(revisit_intent)
    total_score    = mood_score + activity_score + party_fit_score + revisit_score

    return {
        **place,
        "atmosphere":         atmosphere,
        "matched_activities": matched_activities,
        "revisit_intent":     revisit_intent,
        "revisit_reason":     revisit_reason,
        "summary":            summary,
        "mood_score":         mood_score,
        "activity_score":     activity_score,
        "party_fit_score":    party_fit_score,
        "revisit_score":      revisit_score,
        "total_score":        total_score,
    }


# ─── 장소 목록 점수 계산 (전체, 축약 전) ───
def score_places(places: list[dict], llm_map: dict, moods_kr: list[str], companion_kr: str) -> list[dict]:
    scored = [
        _merge_and_score(p, llm_map.get(p["id"], {}), moods_kr, companion_kr)
        for p in places
    ]
    scored.sort(key=lambda p: -p["total_score"])
    return scored


# ─── bucket 그룹 판정 (day_filter.py가 이미 food/cafe/activity로 태깅해둠) ───
def _bucket_group(place: dict) -> str:
    bucket = place.get("bucket", "")
    return bucket if bucket in DAY_SHORTLIST_QUOTA else "activity"


# ─── 하루 당 quota만큼 축약, 점수 순으로만 판단 ───
# quota 기본값은 20개(음식점7/카페3/활동관광10) — "최적 일정 선택" 노드가 검증 실패로
# 롤백할 때(20→30개 확대) 블로그/GPT 재호출 없이 이미 계산된 scored_by_day에서
# 더 큰 quota로 다시 잘라 쓸 수 있도록 파라미터로 열어둠
def select_day_shortlist(scored: list[dict], quota: dict[str, int] = DAY_SHORTLIST_QUOTA) -> list[dict]:
    grouped: dict[str, list[dict]] = {"food": [], "cafe": [], "activity": []}
    for p in scored:
        grouped[_bucket_group(p)].append(p)

    result = []
    for group, group_quota in quota.items():
        ranked = sorted(grouped[group], key=lambda p: -p["total_score"])
        result.extend(ranked[:group_quota])
    return result