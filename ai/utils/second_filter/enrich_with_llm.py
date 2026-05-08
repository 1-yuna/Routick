# ─────────────────────────────────────────────────────────────────────
# enrich_with_llm
# ─────────────────────────────────────────────────────────────────────
# 블로그 snippet → LLM으로 분위기/재방문의사/bucket 등 추출
#
# 흐름:
#   1. 10개씩 묶어서 프롬프트 생성
#   2. LLM 호출 (5번)
#   3. JSON 파싱 후 반환
# ─────────────────────────────────────────────────────────────────────
from prompts.enrich_places import build_prompt
import asyncio
import os
import json
import httpx


# ─── OPENAI KEY ───
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


# ─── LLM 관리 ───
async def enrich_with_llm(
    blog_data: list[dict],
    user_input: dict,
) -> list[dict]:
    chunks = [blog_data[i:i + 10] for i in range(0, len(blog_data), 10)]

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 순차 대신 병렬로
        tasks = [
            call_llm(client, chunk, user_input)
            for chunk in chunks
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    for r in results:
        if isinstance(r, Exception):
            continue
        output.extend(r)
    return output


# ─── LLM 실행 ───
async def call_llm(
    client: httpx.AsyncClient,
    chunk: list[dict],
    user_input: dict,
) -> list[dict]:
    prompt = build_prompt(chunk, user_input)
    resp = await client.post(
        OPENAI_API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8000,
            "temperature": 0.3,
        },
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)