# ─────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────
# LangGraph AI Agent 파이프라인 (v4)
#
# 실행:
#   - 서버 모드: uvicorn main:app --port 8000 --reload  (Spring 연동용)
#     --reload 필수 — 없으면 nodes/*.py 등을 고쳐도
#     이미 메모리에 로드된 이전 함수가 계속 실행됨 (프로세스 재시작 전까지 코드 변경 반영 안 됨)
#   - 테스트 모드: 파이참에서 main.py 우클릭 → Run 'main'
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from langgraph.graph import StateGraph, START, END
from core.state import TravelState, make_initial_state
from nodes.preprocess_input import preprocess_input
from nodes.region_hint import region_hint
from nodes.collect_and_filter_places import collect_and_filter_places
from nodes.enrich_and_score_places import enrich_and_score_places
from nodes.generate_route_candidates import generate_route_candidates
from nodes.select_itinerary import select_itinerary
from nodes.verify_and_respond import verify_and_respond


# ─── 서버가 실제로 최신 코드로 떠 있는지 빠르게 확인용 ───
# "수정한 게 반영이 안 되는 것 같다" 싶을 때
# GET /api/version 찍어보면 재시작이 실제로 됐는지 바로 확인 가능
# (Spring/Postman에서 호출해봐도 됨). 코드 수정할 때마다 문자열 값을 같이 바꿔주세요.
PIPELINE_VERSION = "v4-2026-08-25"


# ─── LangGraph 그래프 빌드 ───
graph_builder = StateGraph(TravelState)

graph_builder.add_node("preprocess_input",          preprocess_input)
graph_builder.add_node("region_hint",               region_hint)
graph_builder.add_node("collect_and_filter_places", collect_and_filter_places)
graph_builder.add_node("enrich_and_score_places",   enrich_and_score_places)
graph_builder.add_node("generate_route_candidates", generate_route_candidates)
graph_builder.add_node("select_itinerary",          select_itinerary)
graph_builder.add_node("verify_and_respond",        verify_and_respond)

graph_builder.add_edge(START,                       "preprocess_input")
graph_builder.add_edge("preprocess_input",          "region_hint")
graph_builder.add_edge("region_hint",               "collect_and_filter_places")
graph_builder.add_edge("collect_and_filter_places", "enrich_and_score_places")
graph_builder.add_edge("enrich_and_score_places",   "generate_route_candidates")
graph_builder.add_edge("generate_route_candidates", "select_itinerary")
graph_builder.add_edge("select_itinerary",          "verify_and_respond")
graph_builder.add_edge("verify_and_respond",        END)

graph = graph_builder.compile()


# ─── FastAPI 서버 (Spring 연동용) ───
app = FastAPI()

# preprocess_input에서 채워지는 내부 키 (요청에 없으면 None으로 초기화)
INTERNAL_KEYS = [
    "companion_kr", "moods_kr", "activities_kr", "transport_kr",
    "duration_kr", "travel_weekday", "final_keywords",
    "name_search_keywords", "days_info",
]


@app.get("/api/version")
async def version():
    return {"version": PIPELINE_VERSION}


# ─── region_hint 결과(day별 권역/앵커) 콘솔 출력 ───
# "권역/앵커가 뭐가 나왔는지 바로 눈으로 보고 싶다" 용도.
# region_hint 노드 자체도 warnings에 남기지만, 파이프라인이 이후 단계(예:
# collect_and_filter_places)에서 예외/빈 결과가 나도 여기서 먼저 찍어두면
# 권역 조회까지는 잘 됐는지 바로 확인 가능.
def _print_region_hint(final_state: dict) -> None:
    days_info = (final_state.get("user_input") or {}).get("days_info") or []
    print("\n🎯 여행 권역 조회 결과 (region_hint)")
    if not days_info:
        print("   (days_info 없음)")
        return
    for d in days_info:
        print(
            f"   day{d.get('day_number')}: region={d.get('region_name')} | "
            f"anchors={d.get('anchor_names')} | fallback={d.get('is_fallback')}"
        )


@app.post("/api/generate")
async def generate(request: dict):
    try:
        for key in INTERNAL_KEYS:
            request.setdefault(key, None)
        request.setdefault("lat", None)
        request.setdefault("lng", None)
        request.setdefault("days", None)

        initial_state = make_initial_state(request)
        final_state = await graph.ainvoke(initial_state)

        _print_region_hint(final_state)

        response = final_state.get("response")
        if not response:
            raise HTTPException(status_code=500, detail="일정 생성에 실패했습니다")
        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()  # 콘솔에 전체 스택트레이스 출력 (원인 파일/줄번호 확인용)
        raise HTTPException(status_code=500, detail=str(e))


# ─── 테스트 입력 (케이스 2: 출발/도착, 1박2일, 자동차) ───
user_input = {
    "route_type":       "endpoint",
    "travel_days":      2,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "active"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              None,
    "lng":              None,
    "days": [
        {
            "day_number":     1,
            "start_lat":      35.1631, "start_lng": 129.1637,
            "start_name":     "해운대역",
            "start_address":  "부산 해운대구 중동 1428",
            "start_place_id": "8362476",
            "mid_lat":        35.1587, "mid_lng": 129.1604,
            "mid_name":       "해운대",
            "end_lat":        35.1602, "end_lng": 129.1607,
            "end_name":       "코오롱씨클라우드호텔",
            "end_address":    "부산 해운대구 우동 1408-5",
            "end_place_id":   "11819137",
        },
        {
            "day_number":     2,
            "start_lat":      35.1602, "start_lng": 129.1607,
            "start_name":     "코오롱씨클라우드호텔",
            "start_address":  "부산 해운대구 우동 1408-5",
            "start_place_id": "11819137",
            "mid_lat":        35.1531, "mid_lng": 129.1186,
            "mid_name":       "광안리",
            "end_lat":        35.1531, "end_lng": 129.1186,
            "end_name":       "광안리해수욕장",
            "end_address":    "부산 수영구 광안해변로 219",
            "end_place_id":   "7913310",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",

    # [preprocess_input] 내부 변환 후 채워지는 값
    "companion_kr":          None,
    "moods_kr":              None,
    "activities_kr":         None,
    "transport_kr":          None,
    "duration_kr":           None,
    "travel_weekday":        None,
    "final_keywords":        None,
    "name_search_keywords":  None,
    "days_info":             None,
}


async def main():
    initial_state = make_initial_state(user_input)
    final_state = await graph.ainvoke(initial_state)

    _print_region_hint(final_state)

    print(f"\n🔎 마지막 단계(step): {final_state.get('step')}")
    print("🔎 경고/진행 로그(warnings):")
    for w in final_state.get("warnings", []):
        print(f"   - {w}")

    print(json.dumps(final_state["response"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())