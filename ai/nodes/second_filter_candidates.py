# ─────────────────────────────────────────────────────────────────────
# second_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# API/LLM + 점수 계산 + 30개 축약
#
# 흐름:
#   1. 네이버 블로그 snippet 수집 (search_naver_blogs)
#   2. LLM으로 카테고리/분위기/구성원/활동/재방문의사/요약 추출 (enrich_with_llm)
#   3. filtered_candidates에 보강 데이터 머지
#   4. 점수 계산 → scored_candidates (scoring)
#   5. 카테고리 quota 분배 → 30개 축약(shortlist)
# ─────────────────────────────────────────────────────────────────────

from utils.second_filter.search_naver_blogs import search_naver_blogs
from utils.second_filter.enrich_with_llm import enrich_with_llm
from utils.second_filter.scoring import calc_mood_score, calc_activity_score, calc_party_fit_score, calc_revisit_score, calc_total_score
from utils.second_filter.shortlist import select_shortlist, classify_fallback
import time


# ─── [노드] 30개 축약  ───
async def second_filter_candidates(state: dict) -> dict:
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

    # 네이버 블로그 snippet 수집 (search_naver_blogs)
    t1 = time.time()
    try:
        blog_data = await search_naver_blogs(filtered)
    except Exception as e:
        warnings.append(f"네이버 블로그 수집 실패: {e}")
        blog_data = []
    print(f"⏱  네이버 블로그: {time.time() - t1:.1f}초 ({len(blog_data)}개)")

    # LLM으로 카테고리/분위기/구성원/활동/재방문의사/요약 추출 (enrich_with_llm)
    t2 = time.time()
    llm_results = []
    if blog_data:
        try:
            llm_results = await enrich_with_llm(blog_data, ui)
        except Exception as e:
            warnings.append(f"LLM 보강 실패: {e}")
    else:
        warnings.append("블로그 데이터 없음 → LLM 스킵")
    print(f"⏱  LLM 보강: {time.time() - t2:.1f}초 ({len(llm_results)}개)")

    # filtered_candidates에 머지
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
            "place_tags": enrich.get("place_tags", []),
            "revisit_intent": enrich.get("revisit_intent", "low"),
            "summary": enrich.get("summary", ""),
        })

    # 점수 계산 (scoring)
    scored = []
    for place in enriched:
        mood_score = calc_mood_score(place, mood_preferences)
        activity_score = calc_activity_score(place, activity_preferences)
        party_fit_score = calc_party_fit_score(place, party_type, party_size, age_group)
        revisit_score = calc_revisit_score(place)
        total_score = calc_total_score(
            mood_score,
            activity_score,
            party_fit_score,
            revisit_score,
        )
        scored.append({
            "place": place,
            "mood_score": mood_score,
            "activity_score": activity_score,
            "party_fit_score": party_fit_score,
            "revisit_score": revisit_score,
            "total_score": total_score,
        })

    # total_score 내림차순 정렬
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # 30개 축약 (select_shortlist)
    shortlist = select_shortlist(scored, duration=duration, target_count=30)

    if not shortlist:
        warnings.append("shortlist 비어있음")

    return {
        "filtered_candidates": enriched, #50개
        "scored_candidates": scored,
        "shortlist": shortlist, # 최종 선별 30
        "warnings": warnings,
        "step": "enriched",
    }