# ─────────────────────────────────────────────────────────────────────
# llm_enrich
# ─────────────────────────────────────────────────────────────────────
# GPT로 블로그 요약 기반 장소 보강
# 추출 항목: 분위기 / 활동(사용자 선호 활동 매칭) / 재방문의사(+근거 및 신뢰도) / 특징요약
# 5개씩 청크로 나눠 병렬 호출 (청크가 작을수록 청크당 생성량이 줄어 개별 응답이 빨라짐)
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
import os

import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

ENRICH_MODEL = "gpt-5-mini"
CHUNK_SIZE   = 5

ATMOSPHERE_TAGS = ["활기찬", "힐링", "감성", "이색", "조용한", "따뜻한", "로맨틱", "깔끔한", "빈티지", "힙한"]


# ─── 청크 분할 ───
def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# ─── 프롬프트 ───
def _build_prompt(chunk: list[dict], activities_kr: list[str]) -> str:
    lines = []
    for i, item in enumerate(chunk, 1):
        snippets = "\n".join(f"  - {s}" for s in item["snippets"]) or "  - 블로그 없음"
        lines.append(
            f"[{i}] {item['name']} (id: {item['place_id']})\n"
            f"  카테고리: {item.get('category', '')}\n{snippets}"
        )
    places_text = "\n\n".join(lines)

    return f"""
    아래는 여행지 장소들의 블로그 리뷰 발췌입니다.
    각 장소에 대해 JSON 배열로만 응답하세요. 설명, 마크다운, 코드블록 금지.

    블로그 내용이 없어도 제거하지 말고 name/category로 추론해서 채우세요.
    모든 필드 필수, 빈 문자열/배열 금지.

    - atmosphere: {", ".join(ATMOSPHERE_TAGS)} 중 최대 3개.
    - matched_activities: 아래 [사용자 선호 활동] 목록 중, 이 장소가 실제로 해당하는 항목만 골라서 반환.
      해당하는 게 없으면 빈 배열.
      [사용자 선호 활동] {", ".join(activities_kr) if activities_kr else "없음"}
    - revisit_intent: high / medium / low. 블로그 리뷰의 긍정/부정 반응, 재방문 언급,
      리뷰 신뢰도(구체성, 개수)를 종합해 판단.
    - revisit_reason: revisit_intent 판단 근거 및 신뢰도를 1문장으로 작성.
    - summary: 장소 특징 요약, 30자 이내 명사형. "~입니다" 금지.

    [응답 형식]
    [
      {{
        "place_id": "장소id",
        "atmosphere": [],
        "matched_activities": [],
        "revisit_intent": "high"|"medium"|"low",
        "revisit_reason": "",
        "summary": ""
      }}
    ]

    {places_text}
    """


# ─── LLM 호출 (청크 1개) ───
async def _call_llm(client: httpx.AsyncClient, chunk: list[dict], activities_kr: list[str]) -> list[dict]:
    prompt = _build_prompt(chunk, activities_kr)
    is_reasoning_model = ENRICH_MODEL.startswith(("gpt-5", "o1", "o3", "o4"))
    payload = {
        "model": ENRICH_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 2500 if is_reasoning_model else 1200,
    }
    if is_reasoning_model:
        # "none"은 gpt-5.1 전용, 그 외 gpt-5 계열(mini/nano 포함)은 "minimal"이 최저 단계
        payload["reasoning_effort"] = "none" if ENRICH_MODEL == "gpt-5.1" else "minimal"
    else:
        payload["temperature"] = 0.3

    resp = await client.post(
        OPENAI_API_URL,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"},
        json=payload,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ─── 블로그 데이터 → GPT 보강 (청크 병렬 처리), place_id → 보강결과 dict 반환 ───
async def enrich_with_llm(blog_data: list[dict], activities_kr: list[str], warnings: list[str]) -> dict:
    if not blog_data:
        return {}

    chunks = _chunk(blog_data, CHUNK_SIZE)
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = await asyncio.gather(
            *[_call_llm(client, chunk, activities_kr) for chunk in chunks],
            return_exceptions=True,
        )

    llm_map: dict[str, dict] = {}
    for chunk, result in zip(chunks, results):
        if isinstance(result, Exception):
            warnings.append(f"GPT 보강 실패 (청크 {len(chunk)}개): {type(result).__name__}: {result}")
            continue
        for r in result:
            pid = r.get("place_id")
            if pid:
                llm_map[pid] = r

    return llm_map