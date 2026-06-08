# ─────────────────────────────────────────────────────────────────────
# shortlist
# ─────────────────────────────────────────────────────────────────────
# scored_candidates → shortlist (travel_days 기반 quota 분배)
#
# 흐름:
#   1. bucket으로 분류 (LLM 우선, 실패 시 classify_fallback)
#   2. travel_days 기반 quota 정의
#   3. quota만큼 점수순으로 선별
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


# ─── travel_days 기반 quota 정의 ───
SHORTLIST_QUOTA = {
    1: {"cafe": 5,  "food": 8,  "activity": 12, "lodging": 0, "other": 5},
    2: {"cafe": 10, "food": 15, "activity": 25, "lodging": 5, "other": 5},
    3: {"cafe": 15, "food": 22, "activity": 40, "lodging": 8, "other": 5},
    4: {"cafe": 20, "food": 30, "activity": 55, "lodging": 10, "other": 5},
}


# ─── shortlist 선별 ───
def select_shortlist(
    scored: list[dict],
    travel_days: int = 1,
) -> list[dict]:
    quotas = SHORTLIST_QUOTA.get(travel_days, SHORTLIST_QUOTA[1])
    target_count = sum(quotas.values())

    # 카테고리별 버킷 분류 (점수순 유지)
    buckets: dict[str, list] = {k: [] for k in quotas}
    for item in scored:
        bucket = item["place"].get("bucket") or classify_fallback(item["place"])
        if bucket not in VALID_BUCKETS:
            bucket = "other"
        buckets[bucket].append(item)

    # quota만큼 상위 N개 선별
    shortlist = []
    for bucket_name, limit in quotas.items():
        shortlist.extend(buckets[bucket_name][:limit])

    # 부족분 점수순으로 보충
    if len(shortlist) < target_count:
        already_in = {id(item) for item in shortlist}
        for item in scored:
            if id(item) not in already_in:
                shortlist.append(item)
                if len(shortlist) >= target_count:
                    break

    shortlist.sort(key=lambda x: x["total_score"], reverse=True)
    return shortlist[:target_count]