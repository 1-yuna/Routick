# ─────────────────────────────────────────────────────────────────────
# collect_and_filter_places
# ─────────────────────────────────────────────────────────────────────
# 장소 수집 + 1차 필터링 노드
#
# 흐름:
#   1. 앵커 이름 해소 (region_hint가 넘긴 anchor_names → place_id/좌표/카테고리)
#      - 기준 좌표 주변 카카오 키워드 검색, 괄호 부가설명 있으면 벗겨서 재시도
#      - 이미 다른 day에서 해소된 place_id는 제외 (day 순서대로 누적)
#   2. 하루 당 장소 수집
#      - 기준 지역 주변 장소 수집 (도보 5km / 자동차 10km)
#      - 앵커 주변 장소 추가 수집 (앵커 place_id가 존재 시, 도보 0.8km / 자동차 2km)
#      - place_id 기준 중복 제거
#   3. 1차 필터링
#      - 제거: 사용자 제외활동 / 여행과 무관한 키워드 / 동일 이름(접미어 무시)·좌표 중복
#        / 동일 브랜드 하루당 최대 1개 / 동일 세부 카테고리(3단계 이상 일치) 하루당 최대 2개
#      - 카페·베이커리 재분류 (other는 activity로 통합)
#      - 앵커 필수 포함 (제거 단계에서 빠졌으면 다시 추가, 단 제외활동에 걸린 경우는 제외)
#      - 하루 당 30개로 축약 (음식점 10 / 카페·베이커리 5 / 활동·관광 15)
# ─────────────────────────────────────────────────────────────────────

import re

import httpx

from utils.pool.kakao_search import search_kakao_by_radius, kakao_keyword_search_radius, parse_kakao_doc
from utils.first_filter.place_filter_pipeline import classify_bucket
from constants.mapping import BASE_COLLECT_RADIUS_KM, ANCHOR_RADIUS_KM
from constants.place_keywords import EXCLUDE_KEYWORDS, EXCLUDE_KEYWORDS_NAME

MAX_ANCHORS = 3
ANCHOR_SEARCH_PAGES = 2

DAY_QUOTA = {"food": 10, "cafe": 5, "activity": 15}


# ─── 앵커 이름 → place_id/좌표/카테고리 해소 ───
async def _resolve_anchors(
    client: httpx.AsyncClient,
    anchor_names: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    avoid_place_ids: set[str],
) -> list[dict]:
    radius_m = min(int(radius_km * 1000), 20000)
    resolved = []
    for name in anchor_names[:MAX_ANCHORS]:
        try:
            docs = await kakao_keyword_search_radius(client, name, lat, lng, radius_m, page=1)
        except Exception:
            continue
        if not docs:
            stripped = re.sub(r"\s*\([^)]*\)", "", name).strip()
            if not stripped or stripped == name:
                continue
            try:
                docs = await kakao_keyword_search_radius(client, stripped, lat, lng, radius_m, page=1)
            except Exception:
                continue
            if not docs:
                continue
        place = parse_kakao_doc(docs[0])
        if place["id"] in avoid_place_ids:
            continue
        resolved.append({
            **place,
            "place_id":   place["id"],
            "query_name": name,
        })
    return resolved


# ─── 브랜드명 정규화 (지점 suffix 제거) ───
def _brand_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\s+\S*(점|지점|호점|본점|직영점|분점)$', '', name)
    return name.strip()


# ─── 하루치 장소 수집: 기준 지역 반경 + 앵커 반경 병합 후 dedup ───
async def _collect_day(
    keywords:  list[str],
    center_lat: float,
    center_lng: float,
    anchors:   list[dict],
    transport: str,
) -> list[dict]:
    radius_km = BASE_COLLECT_RADIUS_KM.get(transport, BASE_COLLECT_RADIUS_KM["walk"])
    anchor_radius_km = ANCHOR_RADIUS_KM.get(transport, ANCHOR_RADIUS_KM["walk"])

    merged: dict[str, dict] = {}

    base_places, _ = await search_kakao_by_radius(
        keywords=keywords, lat=center_lat, lng=center_lng, radius_km=radius_km,
    )
    for p in base_places:
        merged[p["id"]] = p

    for anchor in anchors:
        if not anchor.get("place_id"):
            continue
        anchor_places, _ = await search_kakao_by_radius(
            keywords=keywords, lat=anchor["lat"], lng=anchor["lng"],
            radius_km=anchor_radius_km, pages=ANCHOR_SEARCH_PAGES,
        )
        for p in anchor_places:
            merged[p["id"]] = p
        merged[anchor["place_id"]] = anchor

    return list(merged.values())


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


# ─── 이름 뒤 일반 접미어 제거 (경의선숲길공원 → 경의선숲길) ───
GENERIC_NAME_SUFFIXES = ["공원", "광장", "거리"]

def _normalize_name(name: str) -> str:
    name = (name or "").strip()
    for suf in GENERIC_NAME_SUFFIXES:
        if name.endswith(suf) and len(name) > len(suf):
            return name[: -len(suf)]
    return name


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


# ─── 제거: 동일 브랜드 하루당 최대 2개 ───
def _cap_brand(places: list[dict], max_per_brand: int = 2) -> list[dict]:
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


# ─── 캡 계산 시 같은 그룹으로 묶을 세부 카테고리 동의어 ───
CATEGORY_SYNONYM_GROUPS = {
    "오락실":     "오락실,게임방",
    "게임방,PC방": "오락실,게임방",
}

# ─── 카테고리 상위 3단계 추출 (동의어는 하나의 그룹으로 통합) ───
def _category_prefix(category: str, depth: int = 3) -> str:
    parts = [p.strip() for p in (category or "").split(">")]
    prefix = parts[:depth]
    if prefix:
        prefix[-1] = CATEGORY_SYNONYM_GROUPS.get(prefix[-1], prefix[-1])
    return " > ".join(prefix)


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
def _filter_day(places: list[dict], avoid_activities: list[str], anchors: list[dict]) -> list[dict]:
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


# ─── [노드] 장소 수집 + 1차 필터링 ───
async def collect_and_filter_places(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    transport         = ui.get("transport", "walk")
    avoid_activities  = ui.get("avoid_activities") or []
    keywords          = ui.get("final_keywords") or []
    days_info         = ui.get("days_info") or []

    if not keywords:
        warnings.append("final_keywords 비어있음 → 기본 키워드 사용")
        keywords = ["맛집", "카페"]

    if not days_info:
        return {
            "filtered_candidates": [],
            "filtered_by_day":     {},
            "user_input":          ui,
            "warnings":            warnings + ["days_info 없음 — region_hint 점검 필요"],
            "step":                "filter_failed",
        }

    radius_km = BASE_COLLECT_RADIUS_KM.get(transport, BASE_COLLECT_RADIUS_KM["walk"])

    filtered_by_day: dict[int, list] = {}
    all_filtered:    list[dict]      = []
    used_place_ids:  set[str]        = set()

    async with httpx.AsyncClient(timeout=15.0) as client:
        for day_info in days_info:
            day_number   = day_info["day_number"]
            center_lat   = day_info.get("center_lat")
            center_lng   = day_info.get("center_lng")
            anchor_names = day_info.get("anchor_names") or []

            if center_lat is None or center_lng is None:
                warnings.append(f"day{day_number} 좌표 없음 → 스킵")
                filtered_by_day[day_number] = []
                continue

            anchors = await _resolve_anchors(
                client, anchor_names, center_lat, center_lng, radius_km, used_place_ids,
            )
            if len(anchors) < len(anchor_names):
                resolved_query_names = {a["query_name"] for a in anchors}
                dropped = [n for n in anchor_names if n not in resolved_query_names]
                warnings.append(f"day{day_number} 앵커 일부 해소 실패: {dropped}")
            for a in anchors:
                used_place_ids.add(a["place_id"])
                if a["name"] != a["query_name"]:
                    warnings.append(f"day{day_number} 앵커 이름 불일치: '{a['query_name']}' 요청 → '{a['name']}' 매칭됨")

            places = await _collect_day(keywords, center_lat, center_lng, anchors, transport)
            if not places:
                warnings.append(f"day{day_number} 수집 결과 0개")

            filtered = _filter_day(places, avoid_activities, anchors)

            filtered_by_day[day_number] = filtered
            all_filtered.extend(filtered)
            warnings.append(f"day{day_number} 앵커 {len(anchors)}개 / 수집 {len(places)}개 → 필터링 후 {len(filtered)}개")

    return {
        "filtered_candidates": all_filtered,
        "filtered_by_day":     filtered_by_day,
        "user_input":          ui,
        "warnings":            warnings,
        "step":                "filtered",
    }