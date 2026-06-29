# ─────────────────────────────────────────────────────────────────────
# kakao_search
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API 비동기 검색 헬퍼
#
# 흐름:
#   1. category 검색용 키워드 × 페이지 × (keyword + category) 비동기 병렬 호출
#      - 케이스 1 (only): radius 파라미터
#      - 케이스 2 (endpoint): rect 파라미터
#   2. name 검색용 키워드 × 페이지 비동기 병렬 호출 (keyword 검색만)
#   3. 일부 실패는 warnings에 기록, 성공한 결과만 합침
#   4. 좌표 → 행정구역명 변환 (region/startRegion/endRegion용)
#
# 주의:
#   - Kakao API는 x=경도, y=위도 (보통 (lat, lng) 순서랑 반대)
#   - rect 파라미터: "min_lng,min_lat,max_lng,max_lat" 형식
# ─────────────────────────────────────────────────────────────────────

import asyncio
import os
import httpx

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_BASE    = "https://dapi.kakao.com/v2/local/search"
KAKAO_GEO     = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"

CATEGORY_CODES = {
    "카페":     "CE7",
    "음식점":   "FD6",
    "관광명소": "AT4",
    "문화시설": "CT1",
    "주차장":   "PK6",
}


# ─── 주차장 검색 (radius) ───
async def search_parking_by_radius(
    lat: float,
    lng: float,
    radius_m: int = 500,
) -> list[dict]:
    """장소 근처 주차장(PK6) 검색"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await kakao_category_search_radius(
                client=client,
                category_code="PK6",
                lat=lat,
                lng=lng,
                radius_m=radius_m,
                page=1,
            )
            return [parse_kakao_doc(doc) for doc in resp]
        except Exception:
            return []


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


# ─── 키워드 검색 (rect) ───
async def kakao_keyword_search_rect(
    client: httpx.AsyncClient,
    query: str,
    rect: str,
    page: int = 1,
) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {
        "query": query,
        "rect":  rect,   # "min_lng,min_lat,max_lng,max_lat"
        "page":  page,
        "size":  15,
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


# ─── 카테고리 검색 (rect) ───
async def kakao_category_search_rect(
    client: httpx.AsyncClient,
    category_code: str,
    rect: str,
    page: int = 1,
) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {
        "category_group_code": category_code,
        "rect": rect,
        "page": page,
        "size": 15,
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


# ─── 좌표 → 행정구역명 변환 ───
async def coord_to_region(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
) -> str:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params  = {"x": lng, "y": lat}
    try:
        resp = await client.get(KAKAO_GEO, headers=headers, params=params)
        resp.raise_for_status()
        docs = resp.json().get("documents", [])
        # H(법정동) 타입 우선, 없으면 B(행정동)
        for doc in docs:
            if doc.get("region_type") == "H":
                # 구+동 조합 반환 (예: "마포구 합정동")
                region_2 = doc.get("region_2depth_name", "")
                region_3 = doc.get("region_3depth_name", "")
                return f"{region_2} {region_3}".strip() if region_3 else region_2
        # fallback: 첫 번째 결과
        if docs:
            region_2 = docs[0].get("region_2depth_name", "")
            region_3 = docs[0].get("region_3depth_name", "")
            return f"{region_2} {region_3}".strip() if region_3 else region_2
    except Exception:
        pass
    return ""


# ─── [메인] 단일 day 검색 - category 키워드 (radius) ───
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


# ─── [메인] 단일 day 검색 - name 키워드 (radius) ───
async def search_kakao_by_radius_name(
    name_keywords: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    pages: int = 3,
) -> tuple[list[dict], list[str]]:
    radius_m  = min(int(radius_km * 1000), 20000)
    warnings: list[str] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks  = []
        labels = []

        for kw in name_keywords:
            for page in range(1, pages + 1):
                tasks.append(kakao_keyword_search_radius(client, kw, lat, lng, radius_m, page))
                labels.append(f"name_kw:{kw}:p{page}")

        results = await asyncio.gather(*tasks, return_exceptions=True)

    return _merge_results(results, labels, warnings), warnings


# ─── [메인] 단일 day 검색 - category 키워드 (rect) ───
async def search_kakao_by_rect(
    keywords: list[str],
    rect_min_lat: float,
    rect_min_lng: float,
    rect_max_lat: float,
    rect_max_lng: float,
    category_codes: dict[str, str] = None,
    pages: int = 3,
) -> tuple[list[dict], list[str]]:
    # 카카오 rect: "min_lng,min_lat,max_lng,max_lat"
    rect  = f"{rect_min_lng},{rect_min_lat},{rect_max_lng},{rect_max_lat}"
    warnings: list[str] = []
    codes = category_codes or CATEGORY_CODES

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks  = []
        labels = []

        for kw in keywords:
            for page in range(1, pages + 1):
                tasks.append(kakao_keyword_search_rect(client, kw, rect, page))
                labels.append(f"category_kw:{kw}:p{page}")

                if kw in codes:
                    code = codes[kw]
                    tasks.append(kakao_category_search_rect(client, code, rect, page))
                    labels.append(f"category:{code}:p{page}")

        results = await asyncio.gather(*tasks, return_exceptions=True)

    return _merge_results(results, labels, warnings), warnings


# ─── [메인] 단일 day 검색 - name 키워드 (rect) ───
async def search_kakao_by_rect_name(
    name_keywords: list[str],
    rect_min_lat: float,
    rect_min_lng: float,
    rect_max_lat: float,
    rect_max_lng: float,
    pages: int = 3,
) -> tuple[list[dict], list[str]]:
    # 카카오 rect: "min_lng,min_lat,max_lng,max_lat"
    rect     = f"{rect_min_lng},{rect_min_lat},{rect_max_lng},{rect_max_lat}"
    warnings: list[str] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks  = []
        labels = []

        for kw in name_keywords:
            for page in range(1, pages + 1):
                tasks.append(kakao_keyword_search_rect(client, kw, rect, page))
                labels.append(f"name_kw:{kw}:p{page}")

        results = await asyncio.gather(*tasks, return_exceptions=True)

    return _merge_results(results, labels, warnings), warnings


# ─── 결과 합치기 + dedup ───
def _merge_results(
    results: list,
    labels: list[str],
    warnings: list[str],
) -> list[dict]:
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