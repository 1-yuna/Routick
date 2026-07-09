# ─────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────
# LangGraph AI Agent 파이프라인
#
# 실행:
#   - 서버 모드: uvicorn main:app --port 8000  (Spring 연동용)
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
from nodes.collect_candidate_pool import collect_candidate_pool
from nodes.first_filter_candidates import first_filter_candidates
from nodes.second_filter_candidates import second_filter_candidates
from nodes.generate_candidates import generate_candidates
from nodes.plan_itinerary import plan_itinerary
from nodes.select_itinerary import select_itinerary
from nodes.fetch_details import fetch_details
from nodes.generate_response import generate_response


# ─── LangGraph 그래프 빌드 ───
graph_builder = StateGraph(TravelState)

graph_builder.add_node("preprocess_input",         preprocess_input)
graph_builder.add_node("collect_candidate_pool",   collect_candidate_pool)
graph_builder.add_node("first_filter_candidates",  first_filter_candidates)
graph_builder.add_node("second_filter_candidates", second_filter_candidates)
graph_builder.add_node("generate_candidates",      generate_candidates)
graph_builder.add_node("plan_itinerary",           plan_itinerary)
graph_builder.add_node("select_itinerary",         select_itinerary)
graph_builder.add_node("fetch_details",            fetch_details)
graph_builder.add_node("generate_response",        generate_response)

graph_builder.add_edge(START,                      "preprocess_input")
graph_builder.add_edge("preprocess_input",         "collect_candidate_pool")
graph_builder.add_edge("collect_candidate_pool",   "first_filter_candidates")
graph_builder.add_edge("first_filter_candidates",  "second_filter_candidates")
graph_builder.add_edge("second_filter_candidates", "generate_candidates")
graph_builder.add_edge("generate_candidates",      "plan_itinerary")
graph_builder.add_edge("plan_itinerary",           "select_itinerary")
graph_builder.add_edge("select_itinerary",         "fetch_details")
graph_builder.add_edge("fetch_details",            "generate_response")
graph_builder.add_edge("generate_response",        END)

graph = graph_builder.compile()


# ─── FastAPI 서버 (Spring 연동용) ───
app = FastAPI()

# preprocess_input에서 채워지는 내부 키 (요청에 없으면 None으로 초기화)
INTERNAL_KEYS = [
    "companion_kr", "moods_kr", "activities_kr", "transport_kr",
    "duration_kr", "travel_weekday", "final_keywords",
    "name_search_keywords", "days_info",
]


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

        response = final_state.get("response")
        if not response:
            raise HTTPException(status_code=500, detail="일정 생성에 실패했습니다")
        return response

    except HTTPException:
        raise
    except Exception as e:
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
    print(json.dumps(final_state["response"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())