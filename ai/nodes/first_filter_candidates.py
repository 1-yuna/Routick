# ─────────────────────────────────────────────────────────────────────
# first_filter_candidates
# ─────────────────────────────────────────────────────────────────────
# 1차 필터: candidates → filtered_candidates (최대 50개)
#
# 흐름:
#   - 관련 없는 키워드 제거 후 50개 축약 (place_filter_pipeline)
#       - dislike 키워드 제거
#       - 부적합 키워드 제거
#       - 구성원에 따라 부적합 키워드 제거
#       - 당일치기 경우 숙박 제거
#       - 체인 브랜드 후순위
#       - 카페,음식점 우선 순위로 바꾼 뒤 (필수적으로 포함되어야하기 때문) > 카페, 음식점 수 줄이기
# ─────────────────────────────────────────────────────────────────────


# TODO: 배포 시 삭제
# ─── 디버깅 헬퍼 ───
from utils.first_filter.place_filter_pipeline import (
    filter_by_dislike,
    filter_by_irrelevant,
    filter_by_party,
    filter_by_accommodation,
    filter_by_brand_priority,
    sort_by_priority,
    filter_by_category_cap,
)
from collections import Counter


# ─── 필터 단계별 결과 출력 ───
def _debug_print(label: str, places: list[dict], removed: int = 0) -> None:
    print(f"\n{label}")
    print(f"   {'─' * 50}")
    print(f"   ✂️  제거: {removed}개  |  남은: {len(places)}개")

    # 카테고리 그룹 분포
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    dist = "  ".join(f"{code}:{cnt}" for code, cnt in counts.most_common(6))
    print(f"   📊 카테고리: {dist}")

    if places:
        print("🔍 전체 장소 목록:")

        for idx, p in enumerate(places, start=1):
            code = p.get("category_group_code", "")
            name = p["name"]
            cat = p.get("category", "")

            print(f"{idx:02}. [{code or '---':3}] {name} | {cat}")


# ─── 최종 결과 요약 ───
def _debug_summary(places: list[dict]) -> None:
    print(f"\n{'═' * 60}")
    print(f"✅ 최종 filtered_candidates: {len(places)}개")
    print(f"{'═' * 60}")

    # 전체 카테고리 분포
    counts = Counter(p.get("category_group_code", "(없음)") for p in places)
    print(f"\n📊 카테고리 분포:")
    for code, cnt in counts.most_common():
        bar = "█" * cnt
        print(f"   {code or '(없음)':6} {cnt:3}개  {bar}")

    # 체인 vs 로컬 분포
    chains = sum(1 for p in places if len(p.get("category", "").split(" > ")) >= 4)
    print(f"\n🏪 체인: {chains}개  |  🏠 로컬: {len(places) - chains}개")



# ─── [노드] 50개 축약  ───
def first_filter_candidates(state: dict, debug: bool = False) -> dict:
    ui = state["user_input"]
    candidates = state["candidates"]
    warnings: list[str] = []
    if debug:
        _debug_print("📦 시작", candidates)

    # dislike 제거 필터
    dislike_keywords = ui.get("dislike_keywords") or []
    filtered, removed_dislike = filter_by_dislike(candidates, dislike_keywords)

    if removed_dislike > 0:
        warnings.append(f"dislike 필터로 {removed_dislike}개 제거")

    if debug:
        _debug_print(f"1️⃣  dislike 필터 ({dislike_keywords})", filtered, removed_dislike)

    # 부적합 키워드 제거 필터
    filtered, removed = filter_by_irrelevant(filtered)
    if removed > 0:
        warnings.append(f"부적합 카테고리로 {removed}개 제거")
    if debug:
        _debug_print("2️⃣  부적합 카테고리", filtered, removed)

    # 구성원 기반 부적합 키워드 제거 필터 ───
    party = ui.get("party_type")
    filtered, removed = filter_by_party(filtered, party)
    if removed > 0:
        warnings.append(f"{party} 부적합 키워드로 {removed}개 제거")
    else :
        warnings.append(f"부적합 키워드로 0개 제거")
    if debug:
        _debug_print(f"3️⃣  party='{party}' 필터", filtered, removed)

    # 당일치기 숙박 제거 필터
    if ui.get("duration") == "당일":
        filtered, removed = filter_by_accommodation(filtered)
        if removed > 0:
            warnings.append(f"당일치기로 숙박 {removed}개 제거")
        if debug:
            _debug_print("4️⃣  당일치기 숙박 제거", filtered, removed)

    # 로컬 우선, 체인 후순위 (50개 제외 모두 삭제)
    filtered, removed = filter_by_brand_priority(filtered, max_count=50)
    if removed > 0:
        warnings.append(f"체인점 후순위 처리로 {removed}개 제거")
    if debug:
        _debug_print("5️⃣  체인점 후순위 (50 cap)", filtered, removed)

    # 음식점/카페 우선 정렬 무조건 포함이 되어야하기 때문
    filtered = sort_by_priority(filtered)
    if debug:
        _debug_print("5️⃣ ½ 음식점/카페 우선순위 정렬", filtered, 0)

    # 카페, 음식점 줄이기 - 너무 많아 줄인다
    activity_preferences = ui.get("activity_preferences") or []
    filtered, removed = filter_by_category_cap(filtered, activity_preferences)
    if removed > 0:
        warnings.append(f"카페,음식점 {removed}개 제거")
    if debug:
        _debug_print("6️⃣  카페,음식점 cap", filtered, removed)

    # 50개 cap
    if len(filtered) > 50:
        warnings.append(f"50개로 cap (원본 {len(filtered)}개)")
        filtered = filtered[:50]
    else:
        warnings.append(f"원본 {len(filtered)}개")
    if debug:
        _debug_print("6️⃣  50개로 cap", filtered, removed)
    if debug:
        _debug_summary(filtered)

    return {
        "filtered_candidates": filtered,
        "warnings": warnings,
        "step": "filtered",
    }