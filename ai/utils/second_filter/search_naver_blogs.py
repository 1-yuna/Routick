# ─────────────────────────────────────────────────────────────────────
# search_naver_blogs
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 API로 장소별 snippet 수집
#
# 흐름:
#   1. 장소명으로 검색 쿼리 생성
#   2. 네이버 블로그 API 호출 (순차 호출, rate limit 준수)
#   3. 장소별 snippet 2개씩 반환
# ─────────────────────────────────────────────────────────────────────

import asyncio
import os
import httpx
import re

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"


def clean_html(text: str) -> str:
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return cleaned[:100]


async def fetch_blog_snippets(
        client: httpx.AsyncClient,
        place: dict,
        display: int = 2,
) -> dict:
    name = place.get("name", "")
    query = name.strip()

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
            await asyncio.sleep(0.1)  # 초당 약 10건으로 제한
    return output