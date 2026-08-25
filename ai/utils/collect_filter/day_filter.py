# ─────────────────────────────────────────────────────────────────────
# day_filter
# ─────────────────────────────────────────────────────────────────────
# 1차 필터링: 제거 → 카페·베이커리 재분류 → 앵커 필수 포함 → day 쿼터 축약
# ─────────────────────────────────────────────────────────────────────

import re

from constants.place_keywords import EXCLUDE_KEYWORDS, EXCLUDE_KEYWORDS_NAME

DAY_QUOTA = {"food": 10, "cafe": 5, "activity": 15}

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

# ─── 이름 뒤 일반 접미어 제거 (경의선숲길공원 → 경의선숲길) ───
GENERIC_NAME_SUFFIXES = ["공원", "광장", "거리"]

def _normalize_name(name: str) -> str:
    name = (name or "").strip()
    for suf in GENERIC_NAME_SUFFIXES:
        if name.endswith(suf) and len(name) > len(suf):
            return name[: -len(suf)]
    return name


# ─── 브랜드명 정규화 (지점 suffix 제거) ───
def _brand_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\s+\S*(점|지점|호점|본점|직영점|분점)$', '', name)
    return name.strip()


# ─── 캡 계산 시 같은 그룹으로 묶을 세부 카테고리 동의어 ───
CATEGORY_SYNONYM_GROUPS = {
    "오락실":      "오락실,게임방",
    "게임방,PC방": "오락실,게임방",
}

# ─── 카테고리 상위 3단계 추출 (동의어는 하나의 그룹으로 통합) ───
def _category_prefix(category: str, depth: int = 3) -> str:
    parts = [p.strip() for p in (category or "").split(">")]
    prefix = parts[:depth]
    if prefix:
        prefix[-1] = CATEGORY_SYNONYM_GROUPS.get(prefix[-1], prefix[-1])
    return " > ".join(prefix)


# ─── 제거: 사용자 제외활동 / 무관 키워드 ───
def _remove_excluded(places: list[dict], avoid_activities: list[str]) -> list[dict]:
    filtered = []
    for p in places:
        name     = p.get("name", "") or ""
        category = p.get("category", "") or ""

        if any(kw in name or kw in category for kw in avoid_activities):
            continue
        if any(kw in category for kw in EXCLUDE_KEYWORDS):
            continue
        if any(kw in name for kw in EXCLUDE_KEYWORDS_NAME):
            continue

        filtered.append(p)
    return filtered


# ─── 제거: 동일 이름(접미어 무시) / 동일 좌표 중복 ───
def _dedup_by_name(places: list[dict]) -> list[dict]:
    seen_names:  set[str] = set()
    seen_coords: set[tuple] = set()
    filtered = []
    for p in places:
        name = _normalize_name(p.get("name", ""))
        lat  = p.get("lat")
        lng  = p.get("lng")
        coord = (lat, lng) if lat is not None and lng is not None else None

        if name in seen_names:
            continue
        if coord is not None and coord in seen_coords:
            continue

        seen_names.add(name)
        if coord is not None:
            seen_coords.add(coord)
        filtered.append(p)
    return filtered


# ─── 제거: 동일 브랜드 하루당 최대 1개 ───
def _cap_brand(places: list[dict], max_per_brand: int = 1) -> list[dict]:
    brand_count: dict[str, int] = {}
    filtered = []
    for p in places:
        brand = _brand_name(p.get("name", ""))
        count = brand_count.get(brand, 0)
        if count >= max_per_brand:
            continue
        brand_count[brand] = count + 1
        filtered.append(p)
    return filtered


# ─── 제거: 동일 세부 카테고리(3단계 이상 일치) 하루당 최대 2개 ───
def _cap_category(places: list[dict], max_per_category: int = 2) -> list[dict]:
    category_count: dict[str, int] = {}
    filtered = []
    for p in places:
        key = _category_prefix(p.get("category", ""))
        if not key:
            filtered.append(p)
            continue
        count = category_count.get(key, 0)
        if count >= max_per_category:
            continue
        category_count[key] = count + 1
        filtered.append(p)
    return filtered


# ─── 앵커 필수 포함 (제거 단계에서 빠졌으면 다시 추가) ───
def _ensure_anchors(places: list[dict], anchors: list[dict], avoid_activities: list[str]) -> list[dict]:
    present_ids = {p["id"] for p in places}
    result = list(places)
    for anchor in anchors:
        place_id = anchor.get("place_id")
        if not place_id or place_id in present_ids:
            continue
        name     = anchor.get("name", "") or ""
        category = anchor.get("category", "") or ""
        if any(kw in name or kw in category for kw in avoid_activities):
            continue
        result.append(anchor)
        present_ids.add(place_id)
    return result


# ─── 카페·베이커리 재분류 (bucket 태깅, other는 activity로 통합) ───
def _tag_bucket(places: list[dict]) -> list[dict]:
    tagged = []
    for p in places:
        bucket = classify_bucket(p)
        if bucket == "other":
            bucket = "activity"
        tagged.append({**p, "bucket": bucket})
    return tagged


# ─── 하루 당 30개로 축약 (음식점 10 / 카페·베이커리 5 / 활동·관광 15), 앵커는 무조건 포함 ───
def _cap_quota(places: list[dict], anchor_place_ids: set[str]) -> list[dict]:
    def _bucket_group(p: dict) -> str:
        bucket = p.get("bucket", "")
        code   = p.get("category_group_code", "")
        if bucket == "cafe" or (code == "CE7" and bucket != "activity"):
            return "cafe"
        if bucket == "food" or code == "FD6":
            return "food"
        return "activity"

    anchors_first = sorted(places, key=lambda p: p["id"] not in anchor_place_ids)

    counts: dict[str, int] = {"food": 0, "cafe": 0, "activity": 0}
    filtered = []
    for p in anchors_first:
        group = _bucket_group(p)
        is_anchor = p["id"] in anchor_place_ids
        if not is_anchor and counts[group] >= DAY_QUOTA[group]:
            continue
        counts[group] += 1
        filtered.append(p)
    return filtered


# ─── 하루치 1차 필터링 ───
def filter_day(places: list[dict], avoid_activities: list[str], anchors: list[dict]) -> list[dict]:
    anchor_place_ids = {a["place_id"] for a in anchors if a.get("place_id")}
    # 앵커를 앞으로 정렬 — 이름 중복 제거 시 앵커가 우선 남도록
    ordered = sorted(places, key=lambda p: p["id"] not in anchor_place_ids)

    filtered = _remove_excluded(ordered, avoid_activities)
    filtered = _dedup_by_name(filtered)
    filtered = _cap_brand(filtered, max_per_brand=1)
    filtered = _cap_category(filtered, max_per_category=2)
    filtered = _tag_bucket(filtered)

    anchors_tagged = _tag_bucket(anchors)
    filtered = _ensure_anchors(filtered, anchors_tagged, avoid_activities)

    filtered = _cap_quota(filtered, anchor_place_ids)
    return filtered