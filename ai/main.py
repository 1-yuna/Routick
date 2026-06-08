# ─────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────
# LangGraph AI Agent 파이프라인
#
# 실행: 파이참에서 main.py 우클릭 → Run 'main'
#
# 흐름:
#   1. preprocess_input
#   2. collect_candidate_pool
#   3. first_filter_candidates
#   4. second_filter_candidates
#   5. travel_matrix
#   6. plan_itinerary
#   7. select_itinerary
#   8. generate_response
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from core.state import TravelState, make_initial_state
from nodes.preprocess_input import preprocess_input
from nodes.collect_candidate_pool import collect_candidate_pool
from nodes.first_filter_candidates import first_filter_candidates
from nodes.second_filter_candidates import second_filter_candidates
from nodes.travel_matrix import travel_matrix
from nodes.plan_itinerary import plan_itinerary
from nodes.select_itinerary import select_itinerary
from nodes.generate_response import generate_response


# ─── LangGraph 그래프 빌드 ───
graph_builder = StateGraph(TravelState)

graph_builder.add_node("preprocess_input",         preprocess_input)
graph_builder.add_node("collect_candidate_pool",   collect_candidate_pool)
graph_builder.add_node("first_filter_candidates",  first_filter_candidates)
graph_builder.add_node("second_filter_candidates", second_filter_candidates)
graph_builder.add_node("travel_matrix",            travel_matrix)
graph_builder.add_node("plan_itinerary",           plan_itinerary)
graph_builder.add_node("select_itinerary",         select_itinerary)
graph_builder.add_node("generate_response",        generate_response)

graph_builder.add_edge(START,                      "preprocess_input")
graph_builder.add_edge("preprocess_input",         "collect_candidate_pool")
graph_builder.add_edge("collect_candidate_pool",   "first_filter_candidates")
graph_builder.add_edge("first_filter_candidates",  "second_filter_candidates")
graph_builder.add_edge("second_filter_candidates", "travel_matrix")
graph_builder.add_edge("travel_matrix",            "plan_itinerary")
graph_builder.add_edge("plan_itinerary",           "select_itinerary")
graph_builder.add_edge("select_itinerary",         "generate_response")
graph_builder.add_edge("generate_response",        END)

graph = graph_builder.compile()


# ─── 테스트 입력 ───
user_input = {
    "destination":      "해운대역",
    "lat":              35.1631,
    "lng":              129.1635,
    "travel_days":      2,
    "companion":        "couple",
    "age_group":        "20s",
    "moods":            ["active", "healing", "clean"],
    "activities":       ["thrill/experience", "performance/culture", "entertainment/sports", "nature/walk"],
    "transport":        "walk",
    "avoid_activities": ["노래방"],
    "start_time":       "09:00",
    "end_time":         "22:00",

    "center_lat":       None,
    "center_lng":       None,
    "search_radius_km": None,
    "final_keywords":   None,
    "companion_kr":     None,
    "age_group_kr":     None,
    "moods_kr":         None,
    "activities_kr":    None,
    "transport_kr":     None,
    "duration_kr":      None,
}


async def main():
    initial_state = make_initial_state(user_input)
    final_state = await graph.ainvoke(initial_state)
    print(json.dumps(final_state["response"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())