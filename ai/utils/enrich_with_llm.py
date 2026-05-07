# ─────────────────────────────────────────────────────────────────────
# llm_enrich.py (utils)
# ─────────────────────────────────────────────────────────────────────
# 블로그 snippet → LLM으로 분위기/재방문의사 등 추출
#
# 흐름:
#   1. 25개씩 묶어서 프롬프트 생성
#   2. LLM 호출 (2번)
#   3. JSON 파싱 후 반환
# ─────────────────────────────────────────────────────────────────────
import asyncio
import os
import json
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def build_prompt(blog_data: list[dict]) -> str:
    lines = []
    for i, item in enumerate(blog_data, 1):
        snippets = "\n".join(f"  - {s}" for s in item["snippets"]) or "  - 블로그 없음"
        lines.append(f"""[{i}] {item['name']} (id: {item['place_id']})
{snippets}""")

    places_text = "\n\n".join(lines)

    return f"""아래는 여행지 장소들의 블로그 리뷰 발췌입니다.
각 장소에 대해 JSON 배열로만 응답하세요. 설명, 마크다운 금지.
- atmosphere 은 제시한 단어로만 응답하세요

{places_text}

[응답 형식]
[
  {{
    "place_id": "장소id",
    "atmosphere": ["활기찬"|"힐링"|"감성"|"이색"|"조용한"|"따뜻한"|"로맨틱"|"깔끔한"|"빈티지"|"힙한"],  // 최대 3개
    "best_for": ["연인"|"혼자"|"친구"|"가족"],  // 최대 3개
    "revisit_intent": "high"|"medium"|"low",
    "summary": "한 문장 30자 이내"
  }},
  ...
]"""


async def enrich_with_llm(blog_data: list[dict]) -> list[dict]:
    chunks = [blog_data[i:i + 25] for i in range(0, len(blog_data), 25)]

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 순차 대신 병렬로
        tasks = [call_llm(client, chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    for r in results:
        if isinstance(r, Exception):
            continue
        output.extend(r)
    return output


async def call_llm(client: httpx.AsyncClient, chunk: list[dict]) -> list[dict]:
    prompt = build_prompt(chunk)
    resp = await client.post(
        OPENAI_API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
        },
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)