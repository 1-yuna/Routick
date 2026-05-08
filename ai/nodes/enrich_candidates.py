# ─────────────────────────────────────────────────────────────────────
# enrich_candidates.py (node)
# ─────────────────────────────────────────────────────────────────────
# 데이터 보강 + 점수 계산 노드
#
# 흐름:
#   1. 네이버 블로그 snippet 수집
#   2. LLM으로 분위기/재방문의사/bucket 추출 (25개씩)
#   3. filtered_candidates에 보강 데이터 머지
#   4. 점수 계산 → scored_candidates
#   5. 카테고리 quota 분배 → shortlist (30개)
# ─────────────────────────────────────────────────────────────────────

from utils.search_naver_blogs import search_naver_blogs
from utils.enrich_with_llm import enrich_with_llm
from utils.scoring import calc_mood_score, calc_activity_score, calc_party_fit_score, calc_total_score
from utils.shortlist import select_shortlist, classify_fallback


async def enrich_candidates(state: dict) -> dict:
    filtered = state["filtered_candidates"]
    ui = state["user_input"]
    warnings: list[str] = []

    mood_preferences = ui.get("mood_preferences") or []
    activity_preferences = ui.get("activity_preferences") or []
    party_type = ui.get("party_type", "")
    party_size = ui.get("party_size", 1)
    age_group = ui.get("age_group", "")
    duration = ui.get("duration", "당일")

    if not filtered:
        warnings.append("filtered_candidates 비어있음 → 보강 스킵")
        return {
            "filtered_candidates": filtered,
            "scored_candidates": [],
            "shortlist": [],
            "warnings": warnings,
            "step": "enriched",
        }

    # ─── 1. 네이버 블로그 snippet 수집 ───
    try:
        blog_data = await search_naver_blogs(filtered)
    except Exception as e:
        warnings.append(f"네이버 블로그 수집 실패: {e}")
        blog_data = []

    # ─── 2. LLM으로 분위기/재방문의사/bucket 추출 ───
    llm_results = []
    if blog_data:
        try:
            llm_results = await enrich_with_llm(blog_data)
        except Exception as e:
            warnings.append(f"LLM 보강 실패: {e}")
    else:
        warnings.append("블로그 데이터 없음 → LLM 스킵")

    # ─── 3. filtered_candidates에 머지 ───
    llm_map = {r["place_id"]: r for r in llm_results}

    enriched = []
    for place in filtered:
        place_id = place.get("id")
        enrich = llm_map.get(place_id, {})
        enriched.append({
            **place,
            "bucket": enrich.get("bucket") or classify_fallback(place),
            "atmosphere": enrich.get("atmosphere", []),
            "best_for": enrich.get("best_for", []),
            "revisit_intent": enrich.get("revisit_intent", "low"),
            "summary": enrich.get("summary", ""),
        })

    # ─── 4. 점수 계산 ───
    scored = []
    for place in enriched:
        mood_score = calc_mood_score(place, mood_preferences)
        activity_score = calc_activity_score(place, activity_preferences)
        party_fit_score = calc_party_fit_score(place, party_type, party_size, age_group)
        total_score = calc_total_score(
            mood_score, activity_score, party_fit_score,
            party_type, activity_preferences,
        )
        scored.append({
            "place": place,
            "mood_score": mood_score,
            "activity_score": activity_score,
            "party_fit_score": party_fit_score,
            "total_score": total_score,
        })

    # total_score 내림차순 정렬
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # ─── 5. shortlist (카테고리 quota 분배, 30개) ───
    shortlist = select_shortlist(scored, duration=duration, target_count=30)

    if not shortlist:
        warnings.append("shortlist 비어있음")

    return {
        "filtered_candidates": enriched,
        "scored_candidates": scored,
        "shortlist": shortlist,
        "warnings": warnings,
        "step": "enriched",
    }