# ─────────────────────────────────────────────────────────────────────
# shortlist
# ─────────────────────────────────────────────────────────────────────
# scored_candidates → shortlist
#
# 흐름:
#   1. (endpoint만) 경로 인접성 보정 — start~end 직선에서 멀리 벗어난
#      장소는 total_score에 패널티를 적용해 우선순위를 낮춤
#   2. category_group_code 기반으로 분류 (CE7/FD6/나머지)
#   3. route_type / travel_days 기반 quota 정의
#      - 케이스 1 (only): travel_days별 전체 quota (30/50/70/80개)
#      - 케이스 2 (endpoint): day당 고정 30개
#   4. quota만큼 점수순으로 선별
#   5. 부족분은 점수순으로 보충
# ─────────────────────────────────────────────────────────────────────

import math

# ─── 케이스 1 (only): travel_days별 전체 quota ───
ONLY_SHORTLIST_QUOTA = {
    1: {"CE7": 5,  "FD6": 8,  "other": 17, "total": 30},
    2: {"CE7": 8,  "FD6": 13, "other": 29, "total": 50},
    3: {"CE7": 11, "FD6": 18, "other": 41, "total": 70},
    4: {"CE7": 13, "FD6": 21, "other": 46, "total": 80},
}

# ─── 케이스 1 (only): K-means 분할 후 day당 quota ───
ONLY_DAY_SHORTLIST_QUOTA = {
    1: {"CE7": 5, "FD6": 8, "other": 17, "total": 30},
    2: {"CE7": 4, "FD6": 6, "other": 15, "total": 25},
    3: {"CE7": 4, "FD6": 6, "other": 13, "total": 23},
    4: {"CE7": 3, "FD6": 5, "other": 12, "total": 20},
}

# ─── 케이스 2 (endpoint): day당 고정 quota ───
DAY_SHORTLIST_QUOTA = {"CE7": 5, "FD6": 8, "other": 17, "total": 30}


# ─── Haversine ───
def _haversine(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ─── 점 → 직선(start-end) 수직 거리 계산 ───
def _perpendicular_distance(lat, lng, start_lat, start_lng, end_lat, end_lng):
    # 위경도를 단순 평면 좌표로 근사 (작은 지역 범위에서는 충분히 정확)
    def to_xy(la, ln):
        x = ln * math.cos(math.radians(start_lat))
        y = la
        return x, y

    px, py = to_xy(lat, lng)
    sx, sy = to_xy(start_lat, start_lng)
    ex, ey = to_xy(end_lat, end_lng)

    line_len_sq = (ex - sx) ** 2 + (ey - sy) ** 2
    if line_len_sq == 0:
        return _haversine(lat, lng, start_lat, start_lng)

    t = max(0, min(1, ((px - sx) * (ex - sx) + (py - sy) * (ey - sy)) / line_len_sq))
    closest_x = sx + t * (ex - sx)
    closest_y = sy + t * (ey - sy)

    # 가장 가까운 직선상의 점(closest_x, closest_y)을 다시 위경도로 환산해 haversine 계산
    closest_lat = closest_y
    closest_lng = closest_x / math.cos(math.radians(start_lat))
    return _haversine(lat, lng, closest_lat, closest_lng)


# ─── shortlist 선별 ───
def select_shortlist(
    scored:      list[dict],
    route_type:  str = "endpoint",
    travel_days: int = 1,
    start_lat:   float = None,
    start_lng:   float = None,
    end_lat:     float = None,
    end_lng:     float = None,
) -> list[dict]:

    if route_type == "only":
        quotas = ONLY_SHORTLIST_QUOTA.get(travel_days, ONLY_SHORTLIST_QUOTA[1])
    elif route_type == "only_day":
        quotas = ONLY_DAY_SHORTLIST_QUOTA.get(travel_days, ONLY_DAY_SHORTLIST_QUOTA[1])
    else:
        quotas = DAY_SHORTLIST_QUOTA

    target_count = quotas["total"]

    # category_group_code 기반 분류 (점수순 유지)
    groups: dict[str, list] = {"CE7": [], "FD6": [], "other": []}
    for item in scored:
        code = item["place"].get("category_group_code", "") or ""
        if code == "CE7":
            groups["CE7"].append(item)
        elif code == "FD6":
            groups["FD6"].append(item)
        else:
            groups["other"].append(item)

    # quota만큼 상위 N개 선별
    shortlist = []
    for group_name in ["CE7", "FD6", "other"]:
        limit = quotas.get(group_name, 0)
        shortlist.extend(groups[group_name][:limit])

    # 부족분 점수순으로 보충
    if len(shortlist) < target_count:
        already_in = {id(item) for item in shortlist}
        for item in scored:
            if id(item) not in already_in:
                shortlist.append(item)
                if len(shortlist) >= target_count:
                    break

    shortlist.sort(key=lambda x: x["total_score"], reverse=True)
    return shortlist[:target_count]