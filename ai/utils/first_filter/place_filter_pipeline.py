# ─────────────────────────────────────────────────────────────────────
# place_filter_pipeline
# ─────────────────────────────────────────────────────────────────────
# 장소 bucket 분류 (음식점/카페/활동)
# ─────────────────────────────────────────────────────────────────────

# ─── 체험형 카페 키워드 (CE7이지만 activity로 분류) ───
ACTIVITY_CAFE_KEYWORDS = [
    "보드카페", "만화카페", "만화방", "방탈출", "방탈출카페",
    "애견카페", "고양이카페", "동물카페", "VR카페",
]

# ─── 디저트류 키워드 (FD6이지만 cafe로 분류) ───
CAFE_FOOD_KEYWORDS = ["제과", "베이커리", "디저트", "아이스크림", "도넛"]


# ─── bucket 분류 ───
def classify_bucket(place: dict) -> str:
    code     = place.get("category_group_code", "")
    name     = place.get("name", "") or ""
    category = place.get("category", "") or ""

    if any(kw in category or kw in name for kw in ACTIVITY_CAFE_KEYWORDS):
        return "activity"

    if code == "CE7":
        return "cafe"
    if code == "FD6":
        if any(kw in category for kw in CAFE_FOOD_KEYWORDS):
            return "cafe"
        return "food"
    if code in ("AT4", "CT1"):
        return "activity"
    if any(kw in category for kw in ["음식점", "한식", "양식", "일식", "중식", "분식"]):
        return "food"
    if "카페" in category:
        return "cafe"
    if any(kw in category for kw in ["관광", "문화", "전시", "박물", "체험", "스포츠", "레저", "공원", "해수욕장", "해변"]):
        return "activity"
    return "other"