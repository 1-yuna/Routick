# ─────────────────────────────────────────────────────────────────────
# constraint_check
# ─────────────────────────────────────────────────────────────────────
# 짜여진 일정이 규칙을 위반하는지 체크
#
# 흐름:
#   1. 이동시간 체크 (30분 초과 구간)
#   2. 카테고리 구성 체크 (food 개수 / food 연속 / place_tags 중복)
#   3. 인원 체크 (1인인데 단체 장소)
#   4. 경로 교차 체크 (X자 동선)
#   5. 연속 같은 bucket 체크 (3회 이상)
#   6. 통과 → generate_response
#      실패 → 문제 장소 excluded_ids 추가 → plan_itinerary로 back
#             retry 5회 초과 or shortlist 소진 → second_filter_candidates로 back
# ─────────────────────────────────────────────────────────────────────

from constants.scoring import PARTY_SIZE_PENALTY
from utils.route.route_check import check_route_intersections, check_consecutive_bucket


# ─── [노드] 규칙 위반 체크 ───
def constraint_check(state: dict) -> dict:
    itinerary = state["itinerary"]
    shortlist = state["shortlist"]
    party_size = state["user_input"].get("party_size", 1)
    excluded_ids = list(state.get("excluded_ids", []))
    constraint_retry_count = state.get("constraint_retry_count", 0)

    violations = []
    problem_ids = []

    # ─── 1. 이동시간 체크 ───
    for item in itinerary:
        if item["travel_to_next_minutes"] > 30:
            violations.append({
                "reason": "이동시간 초과",
                "place_id": item["place"]["id"],
                "detail": f"{item['place']['name']} 다음 이동시간 {item['travel_to_next_minutes']}분"
            })
            problem_ids.append(item["place"]["id"])

    # ─── 2. 카테고리 구성 체크 ───
    food_count = sum(1 for item in itinerary if item["place"].get("bucket") == "food")
    if food_count == 0:
        violations.append({
            "reason": "food 없음",
            "place_id": None,
            "detail": "식사 장소가 없음"
        })

    for i in range(len(itinerary) - 1):
        curr = itinerary[i]["place"]
        next_ = itinerary[i + 1]["place"]

        # food → food 연속
        if curr.get("bucket") == "food" and next_.get("bucket") == "food":
            violations.append({
                "reason": "food 연속",
                "place_id": next_["id"],
                "detail": f"food 연속: {curr['name']} → {next_['name']}"
            })
            problem_ids.append(next_["id"])

        # place_tags 교집합 체크
        curr_tags = set(curr.get("place_tags", []))
        next_tags = set(next_.get("place_tags", []))
        overlap = curr_tags & next_tags
        if overlap:
            curr_score = next((s["total_score"] for s in shortlist if s["place"]["id"] == curr["id"]), 0)
            next_score = next((s["total_score"] for s in shortlist if s["place"]["id"] == next_["id"]), 0)
            remove_id = curr["id"] if curr_score < next_score else next_["id"]
            remove_name = curr["name"] if curr_score < next_score else next_["name"]
            violations.append({
                "reason": "place_tags 중복",
                "place_id": remove_id,
                "detail": f"태그 중복 {overlap}: {curr['name']} → {next_['name']} → {remove_name} 제거"
            })
            problem_ids.append(remove_id)

    # ─── 3. 인원 체크 ───
    if party_size == 1:
        penalty_keywords = PARTY_SIZE_PENALTY.get(1, [])
        for item in itinerary:
            place = item["place"]
            name = place.get("name", "")
            category = place.get("category", "")
            if any(kw in name or kw in category for kw in penalty_keywords):
                violations.append({
                    "reason": "인원 부적합",
                    "place_id": place["id"],
                    "detail": f"1인 부적합 장소: {name}"
                })
                problem_ids.append(place["id"])

    # ─── 4. 경로 교차 체크 ───
    violations.extend(check_route_intersections(itinerary))

    # ─── 5. 연속 같은 bucket 체크 ───
    violations.extend(check_consecutive_bucket(itinerary))

    # ─── 결과 판단 ───
    if not violations:
        return {
            "violations": [],
            "excluded_ids": excluded_ids,
            "constraint_retry_count": constraint_retry_count,
            "next_node": "generate_response",
            "step": "constraint_passed",
        }

    # 문제 place_id 누적
    problem_ids = list(set(problem_ids))
    excluded_ids.extend(problem_ids)
    excluded_ids = list(set(excluded_ids))

    # shortlist에서 남은 장소 확인
    remaining = [
        item for item in shortlist
        if item["place"]["id"] not in excluded_ids
    ]

    # retry 5회 초과 or shortlist 소진 → second_filter로 back
    if not remaining or constraint_retry_count >= 5:
        return {
            "violations": violations,
            "excluded_ids": excluded_ids,
            "constraint_retry_count": 0,
            "next_node": "second_filter_candidates",
            "step": "constraint_exhausted",
        }

    return {
        "violations": violations,
        "excluded_ids": excluded_ids,
        "constraint_retry_count": constraint_retry_count + 1,
        "next_node": "plan_itinerary",
        "step": "constraint_failed",
    }