# ─────────────────────────────────────────────────────────────────────
# route_check
# ─────────────────────────────────────────────────────────────────────
# 경로 자연스러움 검증 헬퍼
#
# 흐름:
#   1. 경로 교차 체크 (X자 동선 감지)
#   2. 연속 같은 bucket 체크 (3회 이상 연속)
# ─────────────────────────────────────────────────────────────────────


# ─── 두 선분 교차 여부 판단 ───
def cross(o: tuple, a: tuple, b: tuple) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def segments_intersect(p1: tuple, p2: tuple, p3: tuple, p4: tuple) -> bool:
    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


# ─── 경로 교차 체크 ───
def check_route_intersections(itinerary: list[dict]) -> list[dict]:
    violations = []
    coords = [(item["place"]["lat"], item["place"]["lng"]) for item in itinerary]
    n = len(coords)

    for i in range(n - 1):
        for j in range(i + 2, n - 1):
            if segments_intersect(coords[i], coords[i+1], coords[j], coords[j+1]):
                violations.append({
                    "reason": "경로 교차",
                    "detail": f"{itinerary[i]['place']['name']} → {itinerary[i+1]['place']['name']} "
                              f"와 {itinerary[j]['place']['name']} → {itinerary[j+1]['place']['name']} 교차"
                })

    return violations


# ─── 연속 같은 bucket 체크 (3회 이상) ───
def check_consecutive_bucket(itinerary: list[dict]) -> list[dict]:
    violations = []
    count = 1

    for i in range(1, len(itinerary)):
        curr_bucket = itinerary[i]["place"].get("bucket", "other")
        prev_bucket = itinerary[i-1]["place"].get("bucket", "other")

        # food는 연속 체크 제외 (점심/저녁 연속 가능성 있음)
        if curr_bucket == "food":
            count = 1
            continue

        if curr_bucket == prev_bucket:
            count += 1
            if count >= 3:
                violations.append({
                    "reason": "연속 bucket",
                    "detail": f"{curr_bucket} 3회 이상 연속: {itinerary[i]['place']['name']}"
                })
        else:
            count = 1

    return violations