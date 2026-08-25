# ─────────────────────────────────────────────────────────────────────
# enrich_and_score_places
# ─────────────────────────────────────────────────────────────────────
# 장소 정보 보강 + 점수화 노드
#
# 흐름:
#   1. 네이버 블로그 검색 (utils/enrich_score/blog_search.py)
#      - 1차 필터링을 통과한 일자별 장소 대상, 장소별 블로그 snippet 최대 5개 비동기 수집
#   2. GPT 보강 (utils/enrich_score/llm_enrich.py)
#      - 분위기 / 활동(사용자 선호 활동 매칭) / 재방문의사(+근거 및 신뢰도) / 특징요약 추출
#      - 10개씩 청크로 나눠 병렬 호출
#   3. 점수 계산 + 2차 필터링 (utils/enrich_score/score_filter.py)
#      - 분위기30 + 활동30 + 동행자20 + 재방문의사20 = 100점
#        (동행자는 GPT 보강 없이 카테고리 기반 기본값으로 판단)
#      - 하루 당 20개로 축약 (음식점7 / 카페3 / 활동관광10), 앵커 보호 없이 점수 순으로만 판단
# ─────────────────────────────────────────────────────────────────────

from utils.enrich_score.blog_search import search_naver_blogs
from utils.enrich_score.llm_enrich import enrich_with_llm
from utils.enrich_score.score_filter import score_places, select_day_shortlist


# ─── [노드] 장소 정보 보강 + 점수화 ───
async def enrich_and_score_places(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    moods_kr      = ui.get("moods_kr") or []
    activities_kr = ui.get("activities_kr") or []
    companion_kr  = ui.get("companion_kr", "")

    filtered_by_day = state.get("filtered_by_day") or {}

    if not filtered_by_day:
        return {
            "scored_candidates": [],
            "shortlist":         [],
            "shortlist_by_day":  {},
            "user_input":        ui,
            "warnings":          warnings + ["filtered_by_day 없음 — collect_and_filter_places 점검 필요"],
            "step":              "score_failed",
        }

    all_scored:       list[dict]      = []
    all_shortlist:    list[dict]      = []
    shortlist_by_day: dict[int, list] = {}

    for day_number, places in filtered_by_day.items():
        if not places:
            shortlist_by_day[day_number] = []
            warnings.append(f"day{day_number} 대상 장소 0개 → 스킵")
            continue

        blog_data = await search_naver_blogs(places, warnings)
        llm_map   = await enrich_with_llm(blog_data, activities_kr, warnings)
        scored    = score_places(places, llm_map, moods_kr, companion_kr)
        shortlist = select_day_shortlist(scored)

        all_scored.extend(scored)
        all_shortlist.extend(shortlist)
        shortlist_by_day[day_number] = shortlist
        warnings.append(f"day{day_number} 보강 {len(places)}개 → 2차 필터링 후 {len(shortlist)}개")

    return {
        "scored_candidates": all_scored,
        "shortlist":         all_shortlist,
        "shortlist_by_day":  shortlist_by_day,
        "user_input":        ui,
        "warnings":          warnings,
        "step":              "scored",
    }