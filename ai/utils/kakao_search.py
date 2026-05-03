import asyncio
import os
import httpx

from constants.keywords import KEYWORD_EXPANSIONS


KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_BASE = "https://dapi.kakao.com/v2/local/search"

# 사용자 키워드 -> 카카오 표준 카테고리 코드 매핑
# 매핑 안 된 키워드 (예: "보드게임카페")는 keyword 검색만 수행
CATEGORY_CODES = {
    "카페": "CE7",
    "음식점": "FD6",
    "관광명소": "AT4",
    "문화시설": "CT1",
    "숙박": "AD5",
}

# 키워드 동의어 확장
def expand_keywords(keywords: list[str]) -> list[str]:
    expanded = []
    seen = set()
    for kw in keywords:
        # 매핑 있으면 동의어 리스트, 없으면 원본 그대로
        for ex in KEYWORD_EXPANSIONS.get(kw, [kw]):
            if ex not in seen:
                seen.add(ex)
                expanded.append(ex)
    return expanded

# 카카오 키워드 검색
async def kakao_keyword_search(
    client: httpx.AsyncClient,
    query: str,
    lat: float,
    lng: float,
    radius_m: int,
    page: int = 1,
) -> list[dict]:

    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "query": query,
        "x": lng, # 카카오는 x가 경도(longitude)
        "y": lat, # 카카오는 y가 위도 (latitude)
        "radius": radius_m,
        "page": page,
        "size": 15, # 카카오 API 페이지당 최대값
    }
    resp = await client.get(
        f"{KAKAO_BASE}/keyword.json", headers=headers, params=params
    )
    resp.raise_for_status()
    return resp.json().get("documents", [])


# 카카오 카테고리 검색
async def kakao_category_search(
    client: httpx.AsyncClient,
    category_code: str,
    lat: float,
    lng: float,
    radius_m: int,
    page: int = 1,
) -> list[dict]:

    # 키워드 검색과 비슷하지만, 검색어 대신 카테고리 코드로 조회
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "category_group_code": category_code,
        "x": lng,
        "y": lat,
        "radius": radius_m,
        "page": page,
        "size": 15,
    }
    resp = await client.get(
        f"{KAKAO_BASE}/category.json", headers=headers, params=params
    )
    resp.raise_for_status()
    return resp.json().get("documents", [])


# 응답 변환 (카카오 -> Place dict)
def parse_kakao_doc(doc: dict) -> dict:

    return {
        "id": doc["id"],
        "name": doc["place_name"],
        "category": doc.get("category_name", ""),
        "category_group_code": doc.get("category_group_code", ""),
        "phone": doc.get("phone", ""),
        "address_name": doc.get("address_name", ""),
        "road_address_name": doc.get("road_address_name", ""),
        "lat": float(doc["y"]),
        "lng": float(doc["x"]),
        "place_url": doc.get("place_url", ""),
        # 보강 단계에서 채워질 필드들
        "tags": [],
        "rating": 0.0,
        "avg_stay_minutes": 60,
        "open_hours": {},
    }


# [메인 함수] Kakao Local API (keyword + category) 비동기 검색
# 여러 페이지 결과를 합쳐서 dedup
async def search_kakao_pool(
    keywords: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    pages: int = 3,
) -> tuple[list[dict], list[str]]:

    # 키워드 확장 (동의어 추가)
    expanded_keywords = expand_keywords(keywords)

    radius_m = int(radius_km * 1000)
    radius_m = min(radius_m, 20000)  # Kakao 최대 20km

    warnings: list[str] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        labels = []

        for kw in expanded_keywords:
            for page in range(1, pages + 1):
                # keyword 검색 (모든 확장 키워드)
                tasks.append(
                    kakao_keyword_search(client, kw, lat, lng, radius_m, page)
                )
                labels.append(f"keyword:{kw}:p{page}")

                # category 검색 (매핑 있을 때만)
                if kw in CATEGORY_CODES:
                    code = CATEGORY_CODES[kw]
                    tasks.append(
                        kakao_category_search(client, code, lat, lng, radius_m, page)
                    )
                    labels.append(f"category:{code}:p{page}")

        # 병렬 실행 (실패해도 진행)
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 결과 합치기 + dedup
    seen_ids: set[str] = set()
    places: list[dict] = []

    for label, result in zip(labels, results):
        if isinstance(result, Exception):
            warnings.append(
                f"kakao search failed [{label}]: "
                f"{type(result).__name__}: {result}"
            )
            continue

        for doc in result:
            if doc["id"] in seen_ids:
                continue
            seen_ids.add(doc["id"])
            places.append(parse_kakao_doc(doc))

    return places, warnings