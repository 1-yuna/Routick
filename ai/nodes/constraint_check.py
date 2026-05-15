# ─────────────────────────────────────────────────────────────────────
# constraint_check
# ─────────────────────────────────────────────────────────────────────
# 짜여진 일정이 규칙을 위반하는지 체크
#
# 흐름:
#   1. 이동시간 체크 (30분 초과 구간)
#   2. 카테고리 구성 체크 (food 개수 / food 연속 / place_tags 중복)
#   3. 인원 체크 (1인인데 단체 장소)
#   4. 통과 → generate_response
#      실패 → 문제 장소 excluded_ids 추가 → plan_itinerary로 back
#             shortlist 소진 시 → second_filter_candidates로 back
# ─────────────────────────────────────────────────────────────────────

from constants.scoring import PARTY_SIZE_PENALTY


# ─── [노드] 규칙 위반 체크 ───
def constraint_check(state: dict) -> dict:
    itinerary = state["itinerary"]
    shortlist = state["shortlist"]
    party_size = state["user_input"].get("party_size", 1)
    excluded_ids = list(state.get("excluded_ids", []))
    retry_count = state.get("retry_count", 0)

    violations = []  # 실패 이유 목록
    problem_ids = [] # 문제 장소 place_id 목록

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
    # food 1개 이상 있는가
    food_count = sum(1 for item in itinerary if item["place"].get("bucket") == "food")
    if food_count == 0:
        violations.append({
            "reason": "food 없음",
            "place_id": None,
            "detail": "식사 장소가 없음"
        })

    # food → food 연속 체크 + place_tags 중복 체크
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
            # 점수 낮은 장소를 제거 대상으로
            curr_score = next((i["total_score"] for i in shortlist if i["place"]["id"] == curr["id"]), 0)
            next_score = next((i["total_score"] for i in shortlist if i["place"]["id"] == next_["id"]), 0)
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

    # ─── 결과 판단 ───
    if not violations:
        return {
            "violations": [],
            "excluded_ids": excluded_ids,
            "retry_count": retry_count,
            "next_node": "generate_response",
            "step": "constraint_passed",
        }

    # 문제 place_id 중복 제거
    problem_ids = list(set(problem_ids))
    excluded_ids.extend(problem_ids)
    excluded_ids = list(set(excluded_ids))

    # shortlist에서 excluded_ids 제외하고 남은 장소 확인
    remaining = [
        item for item in shortlist
        if item["place"]["id"] not in excluded_ids
    ]

    if remaining:
        # shortlist에 교체할 장소 있음 → plan_itinerary로 back
        return {
            "violations": violations,
            "excluded_ids": excluded_ids,
            "retry_count": retry_count + 1,
            "next_node": "plan_itinerary",
            "step": "constraint_failed",
        }
    else:
        # shortlist 소진 → second_filter_candidates로 back
        return {
            "violations": violations,
            "excluded_ids": excluded_ids,
            "retry_count": 0,  # retry_count 초기화
            "next_node": "second_filter_candidates",
            "step": "constraint_exhausted",
        }