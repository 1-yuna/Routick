# ─────────────────────────────────────────────────────────────────────
# enrich_candidates.py (node)
# ─────────────────────────────────────────────────────────────────────
# 데이터 보강 노드
#
# 흐름:
#   1. 네이버 블로그 snippet 수집
#   2. LLM으로 분위기/재방문의사 추출 (25개씩)
#   3. filtered_candidates에 보강 데이터 머지
# ─────────────────────────────────────────────────────────────────────

from utils.search_naver_blogs import search_naver_blogs
from utils.enrich_with_llm import enrich_with_llm


async def enrich_candidates(state: dict) -> dict:
    filtered = state["filtered_candidates"]
    warnings: list[str] = []

    if not filtered:
        warnings.append("filtered_candidates 비어있음 → 보강 스킵")
        return {
            "filtered_candidates": filtered,
            "warnings": warnings,
            "step": "enriched",
        }

    # ─── 1. 네이버 블로그 snippet 수집 ───
    try:
        blog_data = await search_naver_blogs(filtered)
    except Exception as e:
        warnings.append(f"네이버 블로그 수집 실패: {e}")
        blog_data = []

    if not blog_data:
        warnings.append("블로그 데이터 없음 → LLM 스킵")
        return {
            "filtered_candidates": filtered,
            "warnings": warnings,
            "step": "enriched",
        }

    # ─── 2. LLM으로 분위기/재방문의사 추출 ───
    try:
        llm_results = await enrich_with_llm(blog_data)
    except Exception as e:
        warnings.append(f"LLM 보강 실패: {e}")
        llm_results = []

    # ─── 3. filtered_candidates에 머지 ───
    llm_map = {r["place_id"]: r for r in llm_results}

    enriched = []
    for place in filtered:
        place_id = place.get("id")
        enrich = llm_map.get(place_id, {})
        enriched.append({
            **place,
            "atmosphere": enrich.get("atmosphere", []),
            "best_for": enrich.get("best_for", []),
            "revisit_intent": enrich.get("revisit_intent", "low"),
            "summary": enrich.get("summary", ""),
        })

    return {
        "filtered_candidates": enriched,
        "warnings": warnings,
        "step": "enriched",
    }