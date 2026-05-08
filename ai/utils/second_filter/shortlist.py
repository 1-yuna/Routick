# ─────────────────────────────────────────────────────────────────────
# shortlist.py (utils)
# ─────────────────────────────────────────────────────────────────────
# scored_candidates → shortlist (카테고리 quota 분배)
#
# 흐름:
#   1. 가게를 5개 bucket(cafe/food/activity/lodging/other)으로 분류
#      - LLM이 분류한 place["bucket"] 우선
#      - 누락 시 classify_fallback(룰베이스)
#   2. duration에 따라 quota 정의 (당일/숙박)
#   3. quota만큼 점수순으로 뽑아서 shortlist 구성
#   4. 부족분은 점수순으로 보충
# ─────────────────────────────────────────────────────────────────────
VALID_BUCKETS = {"cafe", "food", "activity", "lodging", "other"}


# ─── LLM 실패 시 fallback 분류 (룰베이스) ───
def classify_fallback(place: dict) -> str:
    code = place.get("category_group_code", "") or ""
    category = place.get("category", "") or ""

    if code == "AD5" or any(kw in category for kw in ["숙박", "호텔", "게스트하우스", "펜션", "리조트"]):
        return "lodging"
    if code == "FD6" or any(kw in category for kw in ["음식점", "한식", "양식", "일식", "중식"]):
        return "food"
    if code == "CE7" or "카페" in category:
        return "cafe"
    if code in {"AT4", "CT1"} or any(kw in category for kw in ["관광", "문화", "전시", "박물", "체험", "스포츠", "레저"]):
        return "activity"
    return "other"


# ─── duration 기반 quota 정의 ───
def get_quotas(duration: str) -> dict[str, int]:
    if duration == "당일":
        return {"cafe": 8, "food": 8, "activity": 14, "lodging": 0, "other": 5}
    else:
        return {"cafe": 7, "food": 7, "activity": 12, "lodging": 4, "other": 5}


# ─── shortlist 선별 ───
def select_shortlist(
    scored: list[dict],
    duration: str = "당일",
    target_count: int = 30,
) -> list[dict]:
    quotas = get_quotas(duration)

    # 카테고리별 버킷에 분류 (점수순 자동 유지: scored가 이미 정렬돼있음)
    buckets: dict[str, list] = {k: [] for k in quotas}
    for item in scored:
        bucket = item["place"].get("bucket") or classify_fallback(item["place"])
        if bucket not in VALID_BUCKETS:
            bucket = "other"
        buckets[bucket].append(item)

    # quota만큼 상위 N개 뽑기
    shortlist = []
    for bucket_name, limit in quotas.items():
        shortlist.extend(buckets[bucket_name][:limit])

    # 부족하면 점수순으로 보충 (이미 들어간 건 제외)
    if len(shortlist) < target_count:
        already_in = {id(item) for item in shortlist}
        for item in scored:
            if id(item) not in already_in:
                shortlist.append(item)
                if len(shortlist) >= target_count:
                    break

    # 최종적으로 점수 내림차순 정렬 (보기 좋게)
    shortlist.sort(key=lambda x: x["total_score"], reverse=True)

    return shortlist[:target_count]