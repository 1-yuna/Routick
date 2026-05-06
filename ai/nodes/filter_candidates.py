# ─────────────────────────────────────────────────────────────────────
# filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates (최대 50개)
#
# 흐름:
#   1. dislike 키워드 제거방
#   2. 관련 없는 키워드 제거
#   3. (TODO) 당일치기 -> 숙박 제거
#   3. (TODO) 너무 먼 거리 컷
#   4. (TODO) 브랜드 중복 제거 (동 단위 분산)
#   5. 최대 50개로 cap
# ─────────────────────────────────────────────────────────────────────
from constants.keywords import EXCLUDE_KEYWORDS


# dislike 키워드 제거
def filter_by_dislike(
        places: list[dict],
        dislike_keywords: list[str],
) -> tuple[list[dict], int]:

    if not dislike_keywords:
        return places, 0

    filtered = []
    for p in places:
        name = p.get("name", "")
        category = p.get("category", "")

        # dislike 키워드 중 하나라도 이름/카테고리에 들어있으면 제외
        if any(kw in name or kw in category for kw in dislike_keywords):
            continue

        filtered.append(p)

    removed = len(places) - len(filtered)
    return filtered, removed


# 추천에 안 맞는 키워드 제거
def filter_by_irrelevant(places: list[dict]) -> tuple[list[dict], int]:
    filtered = []
    for p in places:
        # 키워드로 제외
        name = p.get("name", "")
        category = p.get("category", "")
        if any(kw in name or kw in category for kw in EXCLUDE_KEYWORDS):
            continue

        filtered.append(p)

    return filtered, len(places) - len(filtered)


# [메인] 필터
def filter_candidates(state: dict) -> dict:
    ui = state["user_input"]
    candidates = state["candidates"]
    warnings: list[str] = []

    # ─── 1. dislike 필터 ───
    dislike_keywords = ui.get("dislike_keywords") or []
    filtered, removed_dislike = filter_by_dislike(candidates, dislike_keywords)

    if removed_dislike > 0:
        warnings.append(f"dislike 필터로 {removed_dislike}개 제거")

    # ─── 2. 관련 없는 키워드 필터 (시스템 기본) ───
    filtered, removed = filter_by_irrelevant(filtered)
    if removed > 0:
        warnings.append(f"부적합 카테고리로 {removed}개 제거")

    # ─── 2. (TODO) 거리 필터 ───
    # ─── 3. (TODO) 브랜드 중복 제거 ───

    # ─── 4. 50개로 cap ───
    if len(filtered) > 50:
        warnings.append(f"50개로 cap (원본 {len(filtered)}개)")
        filtered = filtered[:50]

    return {
        "filtered_candidates": filtered,
        "warnings": warnings,
        "step": "filtered",
    }