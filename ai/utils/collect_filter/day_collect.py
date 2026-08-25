# ─────────────────────────────────────────────────────────────────────
# day_collect
# ─────────────────────────────────────────────────────────────────────
# 카카오 Local API 검색 + 하루치 장소 수집 (기준 지역 반경 + 앵커 반경 병합 후 dedup)
# ─────────────────────────────────────────────────────────────────────

import asyncio
import os

import httpx

from utils.pool.db import upsert_places
from constants.mapping import BASE_COLLECT_RADIUS_KM, ANCHOR_RADIUS_KM

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_BASE    = "https://dapi.kakao.com/v2/local/search"

CATEGORY_CODES = {
    "카페":     "CE7",
    "음식점":   "FD6",
    "관광명소": "AT4",
    "문화시설": "CT1",
    "주차장":   "PK6",
}

ANCHOR_SEARCH_PAGES = 2


# ─── 키워드 검색 (radius) ───
async def kakao_keyword_search_radius(
    client: httpx.AsyncClient,
    query: str,
    lat: float,
    lng: float,
    radius_m: int,
    page: int = 1,
) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {
        "query":  query,
        "x":      lng,
        "y":      lat,
        "radius": radius_m,
        "page":   page,
        "size":   15,
    }
    resp = await client.get(f"{KAKAO_BASE}/keyword.json", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("documents", [])


# ─── 카테고리 검색 (radius) ───
async def kakao_category_search_radius(
    client: httpx.AsyncClient,
    category_code: str,
    lat: float,
    lng: float,
    radius_m: int,
    page: int = 1,
) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {
        "category_group_code": category_code,
        "x":      lng,
        "y":      lat,
        "radius": radius_m,
        "page":   page,
        "size":   15,
    }
    resp = await client.get(f"{KAKAO_BASE}/category.json", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("documents", [])


# ─── 응답 변환 (카카오 → Place dict) ───
def parse_kakao_doc(doc: dict) -> dict:
    return {
        "id":                   doc["id"],
        "name":                 doc["place_name"],
        "category":             doc.get("category_name", ""),
        "category_group_code":  doc.get("category_group_code", ""),
        "phone":                doc.get("phone", ""),
        "address_name":         doc.get("address_name", ""),
        "road_address_name":    doc.get("road_address_name", ""),
        "lat":                  float(doc["y"]),
        "lng":                  float(doc["x"]),
        "place_url":            doc.get("place_url", ""),
        # 보강 단계에서 채워질 필드
        "bucket":               None,
        "atmosphere":           [],
        "best_for":             [],
        "place_tags":           [],
        "revisit_intent":       None,
        "summary":              "",
        # fetch_details에서 채워질 필드
        "src":                  None,
        "status":               None,
        "opening_hours":        None,
    }


# ─── 결과 합치기 + dedup ───
def _merge_results(results: list, labels: list[str], warnings: list[str]) -> list[dict]:
    seen_ids: set[str] = set()
    places:   list[dict] = []

    for label, result in zip(labels, results):
        if isinstance(result, Exception):
            warnings.append(f"kakao search failed [{label}]: {type(result).__name__}: {result}")
            continue
        for doc in result:
            if doc["id"] in seen_ids:
                continue

            # CE7(카페/음료)는 category_name 깊이 2가 "카페"인 것만 통과
            code     = doc.get("category_group_code", "")
            category = doc.get("category_name", "")
            if code == "CE7":
                parts = [p.strip() for p in category.split(">")]
                if len(parts) < 2 or parts[1] != "카페":
                    continue

            seen_ids.add(doc["id"])
            places.append(parse_kakao_doc(doc))

    return places


# ─── 키워드 × 카테고리 반경 검색 ───
async def search_kakao_by_radius(
    keywords: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    category_codes: dict[str, str] = None,
    pages: int = 3,
) -> tuple[list[dict], list[str]]:
    radius_m  = min(int(radius_km * 1000), 20000)
    warnings: list[str] = []
    codes = category_codes or CATEGORY_CODES

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks  = []
        labels = []

        for kw in keywords:
            for page in range(1, pages + 1):
                tasks.append(kakao_keyword_search_radius(client, kw, lat, lng, radius_m, page))
                labels.append(f"category_kw:{kw}:p{page}")

                if kw in codes:
                    code = codes[kw]
                    tasks.append(kakao_category_search_radius(client, code, lat, lng, radius_m, page))
                    labels.append(f"category:{code}:p{page}")

        results = await asyncio.gather(*tasks, return_exceptions=True)

    return _merge_results(results, labels, warnings), warnings


# ─── 하루치 장소 수집: 기준 지역 반경 + 앵커 반경 병합 후 dedup, PostgreSQL upsert ───
async def collect_day_places(
    keywords:  list[str],
    center_lat: float,
    center_lng: float,
    anchors:   list[dict],
    transport: str,
    warnings:  list[str],
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

    places = list(merged.values())

    if places:
        try:
            await upsert_places(places)
        except Exception as e:
            warnings.append(f"DB upsert 실패: {type(e).__name__}: {e}")

    return places