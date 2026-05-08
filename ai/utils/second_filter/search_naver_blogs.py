# ─────────────────────────────────────────────────────────────────────
# naver_blog_search
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 API로 장소별 snippet 수집
#
# 흐름:
#   1. 장소명 + 동 으로 검색 쿼리 생성
#   2. 네이버 블로그 API 호출 (비동기 병렬)
#   3. 장소별 snippet 3개씩 반환
# ─────────────────────────────────────────────────────────────────────
import asyncio
import os
import httpx
import re

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"


def extract_dong(address: str) -> str:
    """주소에서 동 추출 예: '강원특별자치도 강릉시 강문동 산 4-5' → '강문동'"""
    match = re.search(r'\S+동', address)
    return match.group(0) if match else ""


def clean_html(text: str) -> str:
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return cleaned[:100]


async def fetch_blog_snippets(
        client: httpx.AsyncClient,
        place: dict,
        display: int = 2,
) -> dict:
    name = place.get("name", "")
    query = f"{name}".strip()

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": display,
        "sort": "sim",  # 관련도순
    }



    try:
        resp = await client.get(NAVER_BLOG_URL, headers=headers, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        snippets = [clean_html(item.get("description", "")) for item in items]
    except Exception as e:
        snippets = []

    return {
        "place_id": place.get("id"),
        "name": name,
        "category": place.get("category", ""),
        "snippets": snippets,
    }


async def search_naver_blogs(places: list[dict]) -> list[dict]:
    output = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for p in places:
            result = await fetch_blog_snippets(client, p)
            if result:
                output.append(result)
            await asyncio.sleep(0.15)  # 초당 약 6~7건으로 제한
    return output