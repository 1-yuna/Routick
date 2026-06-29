# ─────────────────────────────────────────────────────────────────────
# second_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 + GPT-4o-mini로 장소 데이터 보강
# + 점수 계산 + shortlist 구성
#
# 흐름:
#   1. 네이버 블로그 snippet 수집 (병렬, Semaphore 5)
#   2. 부정 키워드 감지 → 제거
#   3. GPT-4o-mini로 장소 데이터 보강 (name/category + 블로그 리뷰 함께 입력)
#      - is_valid 판단: name/category만으로 여행지 부적합 장소 제거
#      - 보강: 블로그 기반 atmosphere, revisit_intent 등 추출
#        (블로그 없어도 제거하지 않고 name/category로 추론)
#   4. LLM is_valid=false 장소 제거
#   5. LLM 결과 머지 (atmosphere, best_for, place_tags, revisit_intent, summary)
#   6. 점수 계산 (mood + blog + party + revisit = 최대 300점)
#   7. shortlist 선별 (category_group_code 기반 quota)
#      - 케이스 1 (only): travel_days별 전체 quota
#      - 케이스 2 (endpoint): day별 독립, day당 30개 고정
# ─────────────────────────────────────────────────────────────────────

import time
from utils.second_filter.search_naver_blogs import search_naver_blogs
from utils.second_filter.enrich_with_llm import enrich_with_llm
from utils.second_filter.scoring import (
    calc_mood_score,
    calc_party_fit_score,
    calc_revisit_score,
    calc_blog_score,
    calc_total_score,
)
from utils.second_filter.shortlist import select_shortlist


# ─── [노드] 2차 필터링 및 점수화 ───
async def second_filter_candidates(state: dict) -> dict:
    ui       = state["user_input"]
    warnings: list[str] = []

    moods_kr     = ui.get("moods_kr") or []
    companion_kr = ui.get("companion_kr", "")
    activities_kr = ui.get("activities_kr") or []
    travel_days  = ui.get("travel_days", 1)
    route_type   = ui.get("route_type", "endpoint")

    filtered_by_day = state.get("filtered_by_day", {})

    if not filtered_by_day:
        warnings.append("filtered_by_day 비어있음 → 보강 스킵")
        return {
            "scored_candidates":  [],
            "shortlist":          [],
            "shortlist_by_day":   {},
            "warnings":           warnings,
            "step":               "enriched",
        }

    # only 케이스: 전체 풀을 한 번만 보강
    # endpoint 케이스: day별 독립 보강
    if route_type == "only":
        # day1 후보가 전체 공유 풀
        all_filtered = filtered_by_day.get(1, [])
        scored, shortlist = await _enrich_and_score(
            places=all_filtered,
            moods_kr=moods_kr,
            companion_kr=companion_kr,
            activities_kr=activities_kr,
            route_type=route_type,
            travel_days=travel_days,
            warnings=warnings,
            label="only",
        )
        shortlist_by_day = {
            day_number: shortlist
            for day_number in range(1, travel_days + 1)
        }
        all_scored   = scored
        all_shortlist = shortlist

    else:
        all_scored:    list[dict]      = []
        all_shortlist: list[dict]      = []
        shortlist_by_day: dict[int, list] = {}

        for day_number, day_filtered in filtered_by_day.items():
            scored, shortlist = await _enrich_and_score(
                places=day_filtered,
                moods_kr=moods_kr,
                companion_kr=companion_kr,
                activities_kr=activities_kr,
                route_type=route_type,
                travel_days=travel_days,
                warnings=warnings,
                label=f"day{day_number}",
            )
            shortlist_by_day[day_number] = shortlist
            all_scored.extend(scored)
            all_shortlist.extend(shortlist)

    return {
        "user_input":       ui,
        "scored_candidates": all_scored,
        "shortlist":         all_shortlist,
        "shortlist_by_day":  shortlist_by_day,
        "warnings":          warnings,
        "step":              "enriched",
    }


# ─── 보강 + 점수 계산 공통 함수 ───
async def _enrich_and_score(
    places:       list[dict],
    moods_kr:     list[str],
    companion_kr: str,
    activities_kr: list[str],
    route_type:   str,
    travel_days:  int,
    warnings:     list[str],
    label:        str,
) -> tuple[list[dict], list[dict]]:

    if not places:
        warnings.append(f"[{label}] filtered 비어있음 → 스킵")
        return [], []

    # ── 1. 네이버 블로그 snippet 수집 ───────────────────────────────
    t1 = time.time()
    try:
        blog_data = await search_naver_blogs(places)
    except Exception as e:
        warnings.append(f"[{label}] 네이버 블로그 수집 실패: {e}")
        blog_data = []
    print(f"⏱  [{label}] 네이버 블로그: {time.time() - t1:.1f}초 ({len(blog_data)}개)")

    # ── 2. 부정 키워드 감지 → 제거 ──────────────────────────────────
    blog_map = {b["place_id"]: b for b in blog_data}
    negative_ids = {
        b["place_id"] for b in blog_data if b.get("has_negative")
    }
    if negative_ids:
        warnings.append(f"[{label}] 부정 키워드 감지 {len(negative_ids)}개 제거")

    filtered_places = [p for p in places if p["id"] not in negative_ids]

    # ── 3. GPT-4o-mini로 장소 데이터 보강 ───────────────────────────
    t2 = time.time()
    llm_results = []
    if blog_data:
        # 부정 제거된 장소만 보강
        blog_filtered = [b for b in blog_data if b["place_id"] not in negative_ids]
        try:
            llm_results = await enrich_with_llm(blog_filtered, {"companion_kr": companion_kr, "activities_kr": activities_kr})
        except Exception as e:
            warnings.append(f"[{label}] LLM 보강 실패: {e}")
    print(f"⏱  [{label}] LLM 보강: {time.time() - t2:.1f}초 ({len(llm_results)}개)")

    # ── 4. LLM is_valid 기반 제거 ───────────────────────────────────
    llm_map      = {r["place_id"]: r for r in llm_results}
    place_id_map = {p["id"]: p.get("name", p["id"]) for p in filtered_places}

    invalid_ids: set[str] = set()
    for r in llm_results:
        if not r.get("is_valid", True):
            pid  = r["place_id"]
            name = place_id_map.get(pid, pid)
            invalid_ids.add(pid)
            warnings.append(f"[{label}] LLM 제거: {name} - {r.get('invalid_reason', '')}")

    if invalid_ids:
        warnings.append(f"[{label}] LLM is_valid=false {len(invalid_ids)}개 제거")

    filtered_places = [p for p in filtered_places if p["id"] not in invalid_ids]

    # ── 5. LLM 결과 머지 ────────────────────────────────────────────
    VALID_PLACE_TAGS = {
        "이색카페", "오락", "스포츠", "역사/문화",
        "산책로", "해변/바다", "등산/산",
        "전시관/미술관", "서점", "이색체험", "놀이공원", "아쿠아리움", "영화관", "쇼핑",
        "한식", "일식", "양식", "중식", "분식", "고기", "바/술집",
    }

    enriched = []
    for place in filtered_places:
        place_id = place.get("id")
        enrich   = llm_map.get(place_id, {})

        # place_tags 유효성 검사
        place_tags_raw = enrich.get("place_tags", [])
        if isinstance(place_tags_raw, str):
            place_tags_raw = [place_tags_raw] if place_tags_raw else []
        place_tags = [tag for tag in place_tags_raw if tag in VALID_PLACE_TAGS]

        enriched.append({
            **place,
            "atmosphere":     enrich.get("atmosphere", []),
            "best_for":       enrich.get("best_for", []),
            "place_tags":     place_tags,
            "revisit_intent": enrich.get("revisit_intent", "low"),
            "summary":        enrich.get("summary", ""),
        })

    # ── 5. 점수 계산 ────────────────────────────────────────────────
    scored = []
    for place in enriched:
        place_id       = place.get("id")
        blog_info      = blog_map.get(place_id, {})
        positive_count = blog_info.get("positive_count", 0)
        has_negative   = blog_info.get("has_negative", False)

        mood_score      = calc_mood_score(place, moods_kr)
        blog_score      = calc_blog_score(positive_count, has_negative)
        party_fit_score = calc_party_fit_score(place, companion_kr)
        revisit_score   = calc_revisit_score(place)
        total_score     = calc_total_score(mood_score, blog_score, party_fit_score, revisit_score)

        scored.append({
            "place":           place,
            "mood_score":      mood_score,
            "party_fit_score": party_fit_score,
            "revisit_score":   revisit_score,
            "blog_score":      blog_score,
            "total_score":     total_score,
        })

    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # ── 6. shortlist 선별 ────────────────────────────────────────────
    shortlist = select_shortlist(scored, route_type=route_type, travel_days=travel_days)

    if not shortlist:
        warnings.append(f"[{label}] shortlist 비어있음")

    return scored, shortlist