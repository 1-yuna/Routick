# ─────────────────────────────────────────────────────────────────────
# second_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 + GPT-4o-mini로 장소 데이터 보강
# + 점수 계산 + travel_days 기반 동적 shortlist 구성
#
# 흐름:
#   1. 네이버 블로그 snippet 수집 (search_naver_blogs)
#   2. GPT-4o-mini로 장소 데이터 보강 (enrich_with_llm)
#   3. LLM 실패 시 fallback 분류 (classify_fallback)
#   4. 점수 계산 (scoring)
#   5. shortlist 선별 (select_shortlist)
# ─────────────────────────────────────────────────────────────────────

from utils.second_filter.search_naver_blogs import search_naver_blogs
from utils.second_filter.enrich_with_llm import enrich_with_llm
from utils.second_filter.scoring import calc_mood_score, calc_party_fit_score, calc_revisit_score, calc_total_score
from utils.second_filter.shortlist import select_shortlist, classify_fallback
import time


# ─── [노드] 2차 필터링 및 점수화 ───
async def second_filter_candidates(state: dict) -> dict:
    filtered = state["filtered_candidates"]
    ui = state["user_input"]
    warnings: list[str] = []

    moods_kr = ui.get("moods_kr") or []
    activities_kr = ui.get("activities_kr") or []
    companion_kr = ui.get("companion_kr", "")
    age_group = ui.get("age_group", "")
    travel_days = ui.get("travel_days", 1)

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
    t1 = time.time()
    try:
        blog_data = await search_naver_blogs(filtered)
    except Exception as e:
        warnings.append(f"네이버 블로그 수집 실패: {e}")
        blog_data = []
    print(f"⏱  네이버 블로그: {time.time() - t1:.1f}초 ({len(blog_data)}개)")

    # ─── 2. GPT-4o-mini로 장소 데이터 보강 ───
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

    # ─── 3. LLM 결과 머지 + fallback 분류 ───
    llm_map = {r["place_id"]: r for r in llm_results}

    # category_group_code 기반 bucket 강제 매핑
    CODE_TO_BUCKET = {
        "CE7": "cafe",
        "FD6": "food",
        "AD5": "lodging",
        "AT4": "activity",
        "CT1": "activity",
    }

    enriched = []
    for place in filtered:
        place_id = place.get("id")
        enrich = llm_map.get(place_id, {})
        code = place.get("category_group_code", "")
        name = place.get("name", "") or ""
        category_text = place.get("category", "") or ""

        # category_group_code로 bucket 강제 지정 (LLM 결과보다 우선)
        forced_bucket = CODE_TO_BUCKET.get(code)

        # CE7이지만 체험형/테마형이면 activity로 분류
        ACTIVITY_CAFE_KEYWORDS = [
            "보드카페", "만화카페", "만화방", "방탈출", "방탈출카페",
            "애견카페", "고양이카페", "동물카페", "VR카페",
        ]
        if code == "CE7":
            if any(kw in category_text or kw in name for kw in ACTIVITY_CAFE_KEYWORDS):
                forced_bucket = "activity"

        # FD6이지만 베이커리/제과/디저트면 cafe로 분류
        elif code == "FD6":
            if any(kw in category_text for kw in ["제과", "베이커리", "디저트"]):
                forced_bucket = "cafe"

        # category_group_code 없을 때 category 텍스트로 판단
        if not forced_bucket:
            category = place.get("category", "") or ""
            if any(kw in category for kw in ["숙박", "호텔", "게스트하우스", "펜션", "리조트"]):
                forced_bucket = "lodging"
            elif any(kw in category for kw in ["음식점", "한식", "양식", "일식", "중식", "분식"]):
                forced_bucket = "food"
            elif "카페" in category:
                forced_bucket = "cafe"
            elif any(kw in category for kw in ["관광", "문화", "전시", "박물", "체험", "스포츠", "레저", "문화유적", "공원", "해수욕장", "해변"]):
                forced_bucket = "activity"

        bucket = forced_bucket if forced_bucket else (enrich.get("bucket") or classify_fallback(place))

        enriched.append({
            **place,
            "bucket":         bucket,
            "atmosphere":     enrich.get("atmosphere", []),
            "best_for":       enrich.get("best_for", []),
            "place_tags":     enrich.get("place_tags", []),
            "revisit_intent": enrich.get("revisit_intent", "low"),
            "summary":        enrich.get("summary", ""),
        })

    # ─── 4. 점수 계산 ───
    scored = []
    for place in enriched:
        mood_score      = calc_mood_score(place, moods_kr)
        party_fit_score = calc_party_fit_score(place, companion_kr)
        revisit_score   = calc_revisit_score(place)
        total_score     = calc_total_score(mood_score, party_fit_score, revisit_score)

        scored.append({
            "place":           place,
            "mood_score":      mood_score,
            "party_fit_score": party_fit_score,
            "revisit_score":   revisit_score,
            "total_score":     total_score,
        })

    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # ─── 5. shortlist 선별 ───
    shortlist = select_shortlist(scored, travel_days=travel_days)

    if not shortlist:
        warnings.append("shortlist 비어있음")

    return {
        "user_input": ui,
        "filtered_candidates": enriched,
        "scored_candidates": scored,
        "shortlist": shortlist,
        "warnings": warnings,
        "step": "enriched",
    }