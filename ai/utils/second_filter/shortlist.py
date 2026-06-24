# ─────────────────────────────────────────────────────────────────────
# shortlist
# ─────────────────────────────────────────────────────────────────────
# scored_candidates → shortlist
#
# 흐름:
#   1. bucket으로 분류
#   2. route_type / travel_days 기반 quota 정의
#      - 케이스 1 (only): travel_days별 전체 quota (30/50/70/80개)
#      - 케이스 2 (endpoint): day당 고정 30개
#   3. quota만큼 점수순으로 선별
#   4. 부족분은 점수순으로 보충
# ─────────────────────────────────────────────────────────────────────

VALID_BUCKETS = {"cafe", "food", "activity", "other"}


# ─── LLM 실패 시 fallback 분류 (룰베이스) ───
def classify_fallback(place: dict) -> str:
    code     = place.get("category_group_code", "") or ""
    category = place.get("category", "") or ""

    if code == "FD6" or any(kw in category for kw in ["음식점", "한식", "양식", "일식", "중식"]):
        return "food"
    if code == "CE7" or "카페" in category:
        return "cafe"
    if code in {"AT4", "CT1"} or any(kw in category for kw in ["관광", "문화", "전시", "박물", "체험", "스포츠", "레저"]):
        return "activity"
    return "other"


# ─── 케이스 1 (only): travel_days별 전체 quota ───
ONLY_SHORTLIST_QUOTA = {
    1: {"cafe": 5,  "food": 8,  "activity": 17, "other": 0,  "total": 30},
    2: {"cafe": 8,  "food": 13, "activity": 29, "other": 0,  "total": 50},
    3: {"cafe": 11, "food": 18, "activity": 41, "other": 0,  "total": 70},
    4: {"cafe": 13, "food": 21, "activity": 46, "other": 0,  "total": 80},
}

# ─── 케이스 2 (endpoint): day당 고정 quota ───
DAY_SHORTLIST_QUOTA = {"cafe": 5, "food": 8, "activity": 17, "other": 0, "total": 30}


# ─── shortlist 선별 ───
def select_shortlist(
    scored:      list[dict],
    route_type:  str = "endpoint",
    travel_days: int = 1,
) -> list[dict]:

    if route_type == "only":
        quotas = ONLY_SHORTLIST_QUOTA.get(travel_days, ONLY_SHORTLIST_QUOTA[1])
    else:
        quotas = DAY_SHORTLIST_QUOTA

    target_count = quotas["total"]

    # bucket별 분류 (점수순 유지)
    buckets: dict[str, list] = {k: [] for k in ["cafe", "food", "activity", "other"]}
    for item in scored:
        bucket = item["place"].get("bucket") or classify_fallback(item["place"])
        if bucket not in VALID_BUCKETS:
            bucket = "other"
        buckets[bucket].append(item)

    # quota만큼 상위 N개 선별
    shortlist = []
    for bucket_name in ["cafe", "food", "activity", "other"]:
        limit = quotas.get(bucket_name, 0)
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