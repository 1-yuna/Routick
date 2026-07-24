# ─────────────────────────────────────────────────────────────────────
# scoring
# ─────────────────────────────────────────────────────────────────────
# 점수 계산
#
# 흐름:
#   1. mood_score      → 분위기 매칭 비율 기반 (최대 150점)
#   2. blog_score      → 블로그 긍정 언급 빈도 (최대 100점)
#   3. party_fit_score → best_for에 companion 포함 시 (최대 30점)
#   4. revisit_score   → 재방문 의사 (최대 20점)
#   5. hint_bonus      → 힌트 앵커 본인 20 / 앵커 주변 10 (최대 20점) *(v3.1 변경)*
#   total              → 최대 320점
# ─────────────────────────────────────────────────────────────────────

REVISIT_SCORE_MAP = {
    "high":   20,
    "medium": 10,
    "low":    0,
}

# ─── best_for fallback (LLM 실패 시 카테고리 기반 기본값) ───
BEST_FOR_FALLBACK = {
    "CE7": ["연인", "친구", "혼자"],
    "FD6": ["연인", "친구", "가족", "혼자"],
    "AT4": ["연인", "친구", "가족"],
    "CT1": ["연인", "친구", "가족"],
}


# ─── 분위기 점수 (비율 기반, 최대 150점) ───
def calc_mood_score(place: dict, moods_kr: list[str]) -> float:
    atmosphere = place.get("atmosphere", [])
    if not atmosphere or not moods_kr:
        return 0
    matched = sum(1 for m in moods_kr if m in atmosphere)
    return round((matched / len(moods_kr)) * 150, 1)


# ─── 블로그 긍정 언급 빈도 점수 (최대 100점) ───
def calc_blog_score(positive_count: int, has_negative: bool) -> int:
    if has_negative:
        return 0
    if positive_count >= 4:
        return 100
    if positive_count >= 2:
        return 50
    return 0


# ─── 구성원 적합도 점수 (최대 30점) ───
def calc_party_fit_score(place: dict, companion_kr: str) -> int:
    best_for = place.get("best_for", [])
    code     = place.get("category_group_code", "")

    if not best_for:
        best_for = BEST_FOR_FALLBACK.get(code, ["연인", "친구", "가족", "혼자"])

    return 30 if companion_kr in best_for else 0


# ─── 재방문 의사 점수 (최대 20점) ───
def calc_revisit_score(place: dict) -> int:
    intent = place.get("revisit_intent", "low")
    return REVISIT_SCORE_MAP.get(intent, 0)


# ─── 힌트 보너스 (앵커 20 / 앵커 주변 10, 최대 20점) *(v3.1 변경)* ───
# collect_candidate_pool이 달아준 태그 기반 2단계 배점:
#   - is_hint_anchor: 힌트 앵커 본인 → +20
#   - nearest_hint:   앵커 소반경 내에서 수집된 클러스터 장소 → +10
# fallback: 보충 수집(center 반경)으로 들어와 태그가 없는 장소는
#   힌트 장소명과 이름이 겹치면(부분 일치) 앵커로 간주 +20
#   (태그 기반이 우선인 이유: 이름 매칭은 띄어쓰기 차이에 깨짐
#    예: 힌트 "해운대 블루라인파크" vs 카카오 상호 "해운대블루라인파크")
HINT_ANCHOR_BONUS = 20
HINT_NEARBY_BONUS = 10


def calc_hint_bonus(place: dict, hint_keywords: list[str] | None = None) -> int:
    if place.get("is_hint_anchor"):
        return HINT_ANCHOR_BONUS
    if place.get("nearest_hint"):
        return HINT_NEARBY_BONUS
    if hint_keywords:
        # 공백 제거 후 비교 — "도째비골 스카이밸리"(힌트) vs "도째비골스카이밸리"(카카오 상호)
        name = (place.get("name", "") or "").replace(" ", "")
        if name and any(
            h.replace(" ", "") in name or name in h.replace(" ", "")
            for h in hint_keywords if h
        ):
            return HINT_ANCHOR_BONUS
    return 0


# ─── 종합 점수 (최대 320점) ───
def calc_total_score(
        mood_score:      float,
        blog_score:      int,
        party_fit_score: int,
        revisit_score:   int,
        hint_bonus:      int = 0,
) -> float:
    return mood_score + blog_score + party_fit_score + revisit_score + hint_bonus