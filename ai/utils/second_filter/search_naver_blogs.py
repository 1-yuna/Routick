# ─────────────────────────────────────────────────────────────────────
# search_naver_blogs
# ─────────────────────────────────────────────────────────────────────
# 네이버 블로그 API로 장소별 snippet 수집
#
# 흐름:
#   1. 장소명으로 검색 쿼리 생성
#   2. asyncio.Semaphore(5)로 병렬 처리
#   3. 장소별 snippet 5개 수집
#   4. 부정 키워드 감지 여부 함께 반환
# ─────────────────────────────────────────────────────────────────────

import asyncio
import os
import re
import httpx

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_BLOG_URL      = "https://openapi.naver.com/v1/search/blog.json"

# ─── 부정 키워드 ───
NEGATIVE_KEYWORDS = ["비추", "맛없", "최악", "불친절", "형편없", "싸가지"]

# ─── 긍정 키워드 ───
POSITIVE_KEYWORDS = [
    "맛있", "좋았", "추천", "최고", "또 가고", "재방문", "강추", "훌륭",
    "맛집", "인기", "유명", "맛나", "맛좋", "고소", "시원", "감동",
    "만족", "기대이상", "대박", "굿", "좋아", "맛보", "또올", "재방",
    "완벽", "훌륭", "친절", "분위기 좋", "뷰 좋", "맛도 좋", "또 방문",
    "재미", "재밌", "좋아", "즐기"
]


def clean_html(text: str) -> str:
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return cleaned[:150]


async def fetch_blog_snippets(
        client: httpx.AsyncClient,
        place: dict,
        semaphore: asyncio.Semaphore,
        display: int = 5,
) -> dict:
    name = place.get("name", "")

    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query":   name.strip(),
        "display": display,
        "sort":    "sim",
    }

    async with semaphore:
        try:
            resp = await client.get(NAVER_BLOG_URL, headers=headers, params=params)
            resp.raise_for_status()
            items    = resp.json().get("items", [])
            snippets = [clean_html(item.get("description", "")) for item in items]
        except Exception:
            snippets = []

    # 부정/긍정 키워드 감지
    # positive_count: 긍정 키워드가 하나라도 있는 snippet 수 (최대 5개)
    all_text       = " ".join(snippets)
    has_negative   = any(kw in all_text for kw in NEGATIVE_KEYWORDS)
    positive_count = sum(
        1 for snippet in snippets
        if any(kw in snippet for kw in POSITIVE_KEYWORDS)
    )

    return {
        "place_id":      place.get("id"),
        "name":          name,
        "category":      place.get("category", ""),
        "snippets":      snippets,
        "has_negative":  has_negative,      # 부정 키워드 감지 여부
        "positive_count": positive_count,   # 긍정 키워드 감지 수 (blog_score 계산용)
    }


async def search_naver_blogs(places: list[dict]) -> list[dict]:
    semaphore = asyncio.Semaphore(5)  # 동시 5개 병렬 처리
    output    = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks   = [fetch_blog_snippets(client, p, semaphore) for p in places]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            continue
        output.append(result)

    return output