# ─────────────────────────────────────────────────────────────────────
# blog_search
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 검색 + snippet 수집 (비동기, 장소별 최대 5개)
# ─────────────────────────────────────────────────────────────────────

import asyncio
import os
import re

import httpx

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_BLOG_URL      = "https://openapi.naver.com/v1/search/blog.json"

MAX_SNIPPETS     = 5
SNIPPET_MAX_LEN  = 150

# 네이버 검색 API는 초당 약 10건으로 제한 — 동시 요청 수 + 재시도로 429 대응
DISPATCH_INTERVAL = 0.12
MAX_RETRIES        = 3
RETRY_BASE_DELAY    = 0.5

_TAG_RE = re.compile(r"<[^>]+>")


# ─── HTML 태그 제거 + 길이 자르기 ───
def _clean_html(text: str) -> str:
    text = _TAG_RE.sub("", text or "")
    text = (
        text.replace("&quot;", '"')
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
    )
    return text.strip()[:SNIPPET_MAX_LEN]


# ─── 장소 하나에 대한 블로그 snippet 조회 ───
async def _fetch_blog_snippets(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    place: dict,
    warnings: list[str],
) -> dict:
    async with semaphore:
        headers = {
            "X-Naver-Client-Id":     NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        }
        params = {"query": place["name"], "display": MAX_SNIPPETS, "sort": "sim"}
        items = []
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.get(NAVER_BLOG_URL, headers=headers, params=params)
                if resp.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_BASE_DELAY * (attempt + 1))
                        continue
                    warnings.append(f"네이버 블로그 검색 실패 [{place.get('name')}]: 429 재시도 초과")
                    break
                resp.raise_for_status()
                items = resp.json().get("items", [])
                break
            except Exception as e:
                warnings.append(f"네이버 블로그 검색 실패 [{place.get('name')}]: {type(e).__name__}: {e}")
                break

        snippets = [_clean_html(item.get("description", "")) for item in items[:MAX_SNIPPETS]]
        return {
            "place_id": place["id"],
            "name":     place["name"],
            "category": place.get("category", ""),
            "snippets": snippets,
        }


# ─── 장소별 블로그 snippet 병렬 수집 ───
# 동시 요청 수(semaphore)만으로는 요청 완료가 빨라 초당 제한을 쉽게 넘기므로,
# task 생성 자체를 일정 간격으로 늦춰 초당 호출 수를 직접 제어
async def search_naver_blogs(places: list[dict], warnings: list[str]) -> list[dict]:
    semaphore = asyncio.Semaphore(5)
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for i, p in enumerate(places):
            if i > 0:
                await asyncio.sleep(DISPATCH_INTERVAL)
            tasks.append(asyncio.create_task(_fetch_blog_snippets(client, semaphore, p, warnings)))
        results = await asyncio.gather(*tasks)
    return results