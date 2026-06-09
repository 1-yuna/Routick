# ─────────────────────────────────────────────────────────────────────
# select_itinerary
# ─────────────────────────────────────────────────────────────────────
# LLM이 N개 동선 중 유저 취향에 가장 적합한 동선 선택
# + 각 장소별 추천 이유 생성
#
# 흐름:
#   1. 동선 데이터 축약 (토큰 절약)
#   2. LLM 프롬프트 구성 (travel_days만큼 동선 선택 요청)
#   3. LLM 호출
#   4. 각 day별 선택된 동선에 추천 이유 추가
# ─────────────────────────────────────────────────────────────────────

import os
import json
import httpx
from prompts.select_itinerary_prompt import build_prompt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


# ─── 동선 데이터 축약 (핵심 필드만) ───
def summarize_itineraries(itineraries: list[list[dict]]) -> list[dict]:
    result = []
    for idx, itinerary in enumerate(itineraries):
        places = []
        for item in itinerary:
            p = item["place"]
            places.append({
                "place_id":   p["id"],
                "name":       p["name"],
                "bucket":     p.get("bucket", "other"),
                "atmosphere": p.get("atmosphere", []),
                "best_for":   p.get("best_for", []),
                "place_tags": p.get("place_tags", []),
                "summary":    p.get("summary", ""),
                "arrive_at":  item["arrive_at"],
                "leave_at":   item["leave_at"],
            })
        result.append({
            "index": idx,
            "places": places,
        })
    return result


# ─── LLM 호출 ───
async def call_llm(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
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
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        clean = content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


# ─── [노드] 최적 일정 선택 ───
async def select_itinerary(state: dict) -> dict:
    itineraries = state["itineraries"]
    ui = state["user_input"]
    travel_days = ui.get("travel_days", 1)
    warnings = []

    if not itineraries:
        warnings.append("itineraries 비어있음 → select_itinerary 스킵")
        return {
            "selected_itinerary": [],
            "warnings": warnings,
            "step": "selected",
        }

    # ─── 1. 동선 데이터 축약 ───
    summarized = summarize_itineraries(itineraries)

    # ─── 2. LLM 프롬프트 구성 + 호출 ───
    prompt = build_prompt(ui, summarized)

    try:
        result = await call_llm(prompt)
        days_result = result.get("days", [])
    except Exception as e:
        warnings.append(f"LLM 호출 실패: {e} → fallback 사용")
        days_result = [
            {"day_number": d + 1, "selected_index": d % len(itineraries), "reason": "", "recommendation_reasons": []}
            for d in range(travel_days)
        ]

    # ─── 3. 각 day별 선택된 동선에 추천 이유 추가 + 중복 제거 ───
    selected_itinerary = []
    used_place_ids = set()  # 전체 day 통틀어 사용된 place_id

    for day_data in days_result:
        day_number = day_data.get("day_number", 1)
        selected_index = day_data.get("selected_index", 0)
        recommendation_reasons = {
            r["place_id"]: r["reason"]
            for r in day_data.get("recommendation_reasons", [])
        }

        if selected_index >= len(itineraries):
            warnings.append(f"day{day_number} selected_index {selected_index} 범위 초과 → 0번 동선 사용")
            selected_index = 0

        day_itinerary = []
        for item in itineraries[selected_index]:
            pid = item["place"]["id"]

            # 전체 day 통틀어 중복 place_id 제거
            if pid in used_place_ids:
                warnings.append(f"day{day_number} 중복 장소 제거: {item['place']['name']}")
                continue

            used_place_ids.add(pid)
            item_copy = dict(item)
            item_copy["recommendation_reason"] = (
                recommendation_reasons.get(pid, "")
                or item["place"].get("summary", "")
            )
            item_copy["day_number"] = day_number
            day_itinerary.append(item_copy)

        selected_itinerary.append({
            "day_number": day_number,
            "itinerary": day_itinerary,
        })

    return {
        "selected_itinerary": selected_itinerary,
        "warnings": warnings,
        "step": "selected",
    }