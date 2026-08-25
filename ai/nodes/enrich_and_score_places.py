# ─────────────────────────────────────────────────────────────────────
# enrich_and_score_places
# ─────────────────────────────────────────────────────────────────────
# 장소 정보 보강 + 점수화 노드
#
# 흐름:
#   1. 장소를 CHUNK_SIZE 단위로 나눠, 청크별로 네이버 블로그 검색 →
#      (그 청크 블로그 도착 즉시) GPT 보강을 이어 실행 — 청크끼리는 병렬
#      - 블로그: utils/enrich_score/blog_search.py, 장소별 snippet 최대 5개
#      - GPT: utils/enrich_score/llm_enrich.py, 분위기 / 활동(사용자 선호 활동 매칭)
#        / 재방문의사(+근거 및 신뢰도) / 특징요약 추출
#      day 전체 블로그가 다 모일 때까지 기다린 뒤 GPT를 한꺼번에 쏘는 대신,
#      청크 단위로 블로그→GPT를 바로 이어 붙여 두 단계가 겹치도록 함
#   2. 점수 계산 + 2차 필터링 (utils/enrich_score/score_filter.py)
#      - 분위기30 + 활동30 + 동행자20 + 재방문의사20 = 100점
#        (동행자는 GPT 보강 없이 카테고리 기반 기본값으로 판단)
#      - 하루 당 20개로 축약 (음식점7 / 카페3 / 활동관광10), 앵커 보호 없이 점수 순으로만 판단
#
# day별로 서로 의존성이 없어(collect_and_filter_places와 달리 day 간 dedup 없음)
# 전체를 day별 병렬로 처리 — wall time이 day 수 합산이 아닌 가장 느린 day 1개 기준
# ─────────────────────────────────────────────────────────────────────

import asyncio

from utils.enrich_score.blog_search import search_naver_blogs
from utils.enrich_score.llm_enrich import enrich_chunk_with_llm, CHUNK_SIZE
from utils.enrich_score.score_filter import score_places, select_day_shortlist


# ─── 리스트를 size 단위로 분할 ───
def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# ─── 청크 하나 처리: 블로그 검색 → (도착 즉시) GPT 보강 ───
async def _process_chunk(chunk_places: list[dict], activities_kr: list[str], warnings: list[str]) -> dict:
    blog_data = await search_naver_blogs(chunk_places, warnings)
    return await enrich_chunk_with_llm(blog_data, activities_kr, warnings)


# ─── day 하나 처리: 청크별 블로그→GPT 파이프라인(청크끼리 병렬) → 점수화 → 2차 필터링 ───
async def _process_day(
    day_number: int,
    places: list[dict],
    moods_kr: list[str],
    activities_kr: list[str],
    companion_kr: str,
) -> tuple[int, list[dict], list[dict], list[str]]:
    day_warnings: list[str] = []

    if not places:
        return day_number, [], [], [f"day{day_number} 대상 장소 0개 → 스킵"]

    chunks = _chunk(places, CHUNK_SIZE)
    chunk_maps = await asyncio.gather(*[
        _process_chunk(chunk, activities_kr, day_warnings) for chunk in chunks
    ])

    llm_map: dict[str, dict] = {}
    for m in chunk_maps:
        llm_map.update(m)

    scored    = score_places(places, llm_map, moods_kr, companion_kr)
    shortlist = select_day_shortlist(scored)

    day_warnings.append(f"day{day_number} 보강 {len(places)}개 → 2차 필터링 후 {len(shortlist)}개")
    return day_number, scored, shortlist, day_warnings


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

    results = await asyncio.gather(*[
        _process_day(day_number, places, moods_kr, activities_kr, companion_kr)
        for day_number, places in filtered_by_day.items()
    ])

    all_scored:       list[dict]      = []
    all_shortlist:    list[dict]      = []
    shortlist_by_day: dict[int, list] = {}

    for day_number, scored, shortlist, day_warnings in results:
        all_scored.extend(scored)
        all_shortlist.extend(shortlist)
        shortlist_by_day[day_number] = shortlist
        warnings.extend(day_warnings)

    return {
        "scored_candidates": all_scored,
        "shortlist":         all_shortlist,
        "shortlist_by_day":  shortlist_by_day,
        "user_input":        ui,
        "warnings":          warnings,
        "step":              "scored",
    }