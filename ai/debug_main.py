# ─────────────────────────────────────────────────────────────────────
# debug_main
# ─────────────────────────────────────────────────────────────────────
# 각 노드를 순차 직접 호출해서 어느 단계에서 비어버리는지 확인
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from core.state import make_initial_state
from nodes.preprocess_input import preprocess_input
from nodes.collect_candidate_pool import collect_candidate_pool
from nodes.first_filter_candidates import first_filter_candidates
from nodes.second_filter_candidates import second_filter_candidates
from nodes.generate_candidates import generate_candidates
from nodes.plan_itinerary import plan_itinerary
from nodes.select_itinerary import select_itinerary
from nodes.fetch_details import fetch_details
from nodes.generate_response import generate_response

from main import user_input  # main.py의 user_input 재사용


async def main():
    initial_state = make_initial_state(user_input)

    print("=== 1. preprocess_input ===")
    r1 = preprocess_input(initial_state)
    print("step:", r1["step"], "| warnings:", r1["warnings"])

    print("\n=== 2. collect_candidate_pool ===")
    s2 = {**initial_state, "user_input": r1["user_input"]}
    r2 = await collect_candidate_pool(s2)
    print("step:", r2["step"], "| warnings:", r2["warnings"])
    print("candidates 수:", len(r2["candidates"]))
    for d, places in r2["candidates_by_day"].items():
        print(f"  day{d}: {len(places)}개")

    print("\n=== 3. first_filter_candidates ===")
    s3 = {**initial_state, "user_input": r2["user_input"], "candidates": r2["candidates"], "candidates_by_day": r2["candidates_by_day"]}
    r3 = first_filter_candidates(s3)
    print("step:", r3["step"], "| warnings:", r3["warnings"])
    for d, places in r3["filtered_by_day"].items():
        print(f"  day{d}: {len(places)}개")

    print("\n=== 4. second_filter_candidates ===")
    s4 = {**initial_state, "user_input": r3["user_input"], "filtered_candidates": r3["filtered_candidates"], "filtered_by_day": r3["filtered_by_day"]}
    r4 = await second_filter_candidates(s4)
    print("step:", r4["step"], "| warnings:", r4["warnings"])
    for d, sl in r4["shortlist_by_day"].items():
        print(f"  day{d}: {len(sl)}개")

    print("\n=== 5. generate_candidates ===")
    s5 = {**initial_state, "user_input": r4["user_input"], "shortlist_by_day": r4["shortlist_by_day"], "excluded_place_ids": []}
    r5 = generate_candidates(s5)
    print("step:", r5["step"], "| warnings:", r5["warnings"])
    for d, routes in r5["valid_routes_by_day"].items():
        print(f"  day{d} 유효 동선: {len(routes)}개")

    print("\n=== 6. plan_itinerary ===")
    s6 = {**initial_state, "user_input": r5.get("user_input", r4["user_input"]), "valid_routes_by_day": r5["valid_routes_by_day"], "all_routes_by_day": r5["all_routes_by_day"]}
    r6 = await plan_itinerary(s6)
    print("step:", r6["step"], "| warnings:", r6["warnings"])
    for d, its in r6["itineraries_by_day"].items():
        print(f"  day{d}: {len(its)}개 후보")

    print("\n=== 7. select_itinerary ===")
    s7 = {**initial_state, "user_input": r4["user_input"], "itineraries_by_day": r6["itineraries_by_day"], "excluded_place_ids": [], "rollback_count": 0}
    r7 = await select_itinerary(s7)
    print("step:", r7["step"], "| warnings:", r7["warnings"])
    if r7["step"] != "itinerary_selected":
        print("🚨 여기서 멈춤! final_itineraries:", r7.get("final_itineraries"))
        return
    for d, it in r7["final_itineraries"].items():
        print(f"  day{d}: {len(it)}개 아이템")

    print("\n=== 8. fetch_details ===")
    s8 = {**initial_state, "user_input": r4["user_input"], "final_itineraries": r7["final_itineraries"], "shortlist_by_day": r4["shortlist_by_day"], "filtered_by_day": r3["filtered_by_day"]}
    r8 = await fetch_details(s8)
    print("step:", r8["step"], "| warnings:", r8["warnings"])
    for d, it in r8["final_itineraries"].items():
        print(f"  day{d}: {len(it)}개 아이템")

    print("\n=== 9. generate_response ===")
    s9 = {
        **initial_state,
        "user_input": r8.get("user_input", r4["user_input"]),
        "selected_itinerary": [
            {"day_number": d, "itinerary": it} for d, it in r8["final_itineraries"].items()
        ],
    }
    r9 = generate_response(s9)
    print("step:", r9["step"], "| warnings:", r9["warnings"])
    print(json.dumps(r9["response"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())