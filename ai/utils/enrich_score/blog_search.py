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

# 네이버 검색 API는 초당 약 10건으로 제한 — day별로 이 함수가 동시에 여러 번
# 호출돼도(엔진 전체 기준) 초당 호출 수를 넘기지 않도록 전역 dispatch gate로 제어
# 0.10초 = 초당 10건, 문서상 한도에 거의 붙임 (429나면 재시도가 받아줌)
DISPATCH_INTERVAL = 0.10
MAX_RETRIES        = 3
RETRY_BASE_DELAY    = 0.5

_dispatch_lock: asyncio.Lock | None = None
_next_dispatch_time = 0.0


# ─── 전역 dispatch gate: 프로세스 전체 기준으로 요청 간격 확보 (day 병렬 호출 포함) ───
async def _acquire_dispatch_slot() -> None:
    global _dispatch_lock, _next_dispatch_time
    if _dispatch_lock is None:
        _dispatch_lock = asyncio.Lock()

    async with _dispatch_lock:
        loop = asyncio.get_event_loop()
        now = loop.time()
        start_at = max(_next_dispatch_time, now)
        _next_dispatch_time = start_at + DISPATCH_INTERVAL
        wait = start_at - now

    if wait > 0:
        await asyncio.sleep(wait)


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
            await _acquire_dispatch_slot()
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
# 실제 초당 호출 수 제어는 _acquire_dispatch_slot()이 전역으로 담당하므로
# 여기서는 동시 커넥션 수만 semaphore로 적당히 제한
async def search_naver_blogs(places: list[dict], warnings: list[str]) -> list[dict]:
    semaphore = asyncio.Semaphore(8)
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [_fetch_blog_snippets(client, semaphore, p, warnings) for p in places]
        results = await asyncio.gather(*tasks)
    return results