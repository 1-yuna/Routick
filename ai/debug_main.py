# ─────────────────────────────────────────────────────────────────────
# debug_main
# ─────────────────────────────────────────────────────────────────────
# 각 노드를 순차 직접 호출해서 어느 단계에서 비어버리는지 확인 (v4, 7단계)
# ─────────────────────────────────────────────────────────────────────

import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from core.state import make_initial_state
from nodes.preprocess_input import preprocess_input
from nodes.region_hint import region_hint
from nodes.collect_and_filter_places import collect_and_filter_places
from nodes.enrich_and_score_places import enrich_and_score_places
from nodes.generate_route_candidates import generate_route_candidates
from nodes.select_itinerary import select_itinerary
from nodes.verify_and_respond import verify_and_respond

from main import user_input  # main.py의 user_input 재사용


async def main():
    initial_state = make_initial_state(user_input)

    print("=== 1. preprocess_input ===")
    r1 = preprocess_input(initial_state)
    print("step:", r1["step"], "| warnings:", r1["warnings"])

    print("\n=== 2. region_hint ===")
    s2 = {**initial_state, "user_input": r1["user_input"]}
    r2 = await region_hint(s2)
    print("step:", r2["step"], "| warnings:", r2["warnings"])
    for d in (r2["user_input"].get("days_info") or []):
        print(
            f"  day{d.get('day_number')}: region={d.get('region_name')} | "
            f"anchors={d.get('anchor_names')} | fallback={d.get('is_fallback')}"
        )
    if not (r2["user_input"].get("days_info") or []):
        print("🚨 여기서 멈춤! days_info 비어있음")
        return

    print("\n=== 3. collect_and_filter_places ===")
    s3 = {**initial_state, "user_input": r2["user_input"]}
    r3 = await collect_and_filter_places(s3)
    print("step:", r3["step"], "| warnings:", r3["warnings"])
    for d, places in r3["filtered_by_day"].items():
        print(f"  day{d}: {len(places)}개")
    if not r3["filtered_by_day"]:
        print("🚨 여기서 멈춤! filtered_by_day 비어있음")
        return

    print("\n=== 4. enrich_and_score_places ===")
    s4 = {**initial_state, "user_input": r3["user_input"], "filtered_by_day": r3["filtered_by_day"]}
    r4 = await enrich_and_score_places(s4)
    print("step:", r4["step"], "| warnings:", r4["warnings"])
    for d, sl in r4["shortlist_by_day"].items():
        print(f"  day{d}: {len(sl)}개")
    if not r4["shortlist_by_day"]:
        print("🚨 여기서 멈춤! shortlist_by_day 비어있음")
        return

    print("\n=== 5. generate_route_candidates ===")
    s5 = {**initial_state, "user_input": r4["user_input"], "shortlist_by_day": r4["shortlist_by_day"]}
    r5 = await generate_route_candidates(s5)
    print("step:", r5["step"], "| warnings:", r5["warnings"])
    for d, routes in r5["route_candidates_by_day"].items():
        print(f"  day{d}: 동선 {len(routes)}개")
    if not r5["route_candidates_by_day"]:
        print("🚨 여기서 멈춤! route_candidates_by_day 비어있음")
        return

    print("\n=== 6. select_itinerary ===")
    s6 = {
        **initial_state,
        "user_input":              r5["user_input"],
        "route_candidates_by_day": r5["route_candidates_by_day"],
        "scored_by_day":           r4["scored_by_day"],
    }
    r6 = await select_itinerary(s6)
    print("step:", r6["step"], "| warnings:", r6["warnings"])
    if r6["step"] != "itinerary_selected":
        print("🚨 여기서 멈춤! final_itineraries:", r6.get("final_itineraries"))
        return
    for d, route in r6["final_itineraries"].items():
        print(f"  day{d}: 총점 {route['total_score']}점 / 장소 {len(route['places'])}개 / 앵커 {'✅' if route['has_anchor'] else '❌'}")

    print("\n=== 7. verify_and_respond ===")
    s7 = {
        **initial_state,
        "user_input":        r6["user_input"],
        "final_itineraries": r6["final_itineraries"],
        "scored_by_day":     r4["scored_by_day"],
    }
    r7 = await verify_and_respond(s7)
    print("step:", r7["step"], "| warnings:", r7["warnings"])
    if r7["step"] != "done":
        print("🚨 여기서 멈춤! response:", r7.get("response"))
        return
    print(json.dumps(r7["response"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())