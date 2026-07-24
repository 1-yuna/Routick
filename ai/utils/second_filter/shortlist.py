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
#   4. *(v3.1 신규)* 힌트 앵커(is_hint_anchor 태그, 또는 태그 없으면
#      hint_keywords 이름 완전일치 fallback)는 quota 계산 전에 먼저
#      무조건 확보 — "other" 버킷처럼 quota가 빡빡한 그룹에서 나머지
#      점수 높은 activity 후보들에 밀려 힌트가 탈락하는 문제 방지.
#      (hint_bonus로 점수만 얹어주는 것으로는 quota가 꽉 찬 그룹에서
#       보장이 안 됨 — 반드시 quota와 무관하게 슬롯을 확보해야 함)
#   5. quota만큼 점수순으로 선별 (힌트로 이미 채워진 만큼 quota 차감)
#   6. 부족분은 점수순으로 보충
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


# ─── 힌트 보호 판정 (태그 + 이름 완전일치 fallback) ───
# place_filter_pipeline._is_hint_protected와 동일 원칙(공백 제거 후 완전
# 일치만 인정 — "삼척항"처럼 짧은 힌트가 무관한 상호에 부분매칭되는 것 방지)
def _is_hint_protected(place: dict, hint_kws: list[str]) -> bool:
    if place.get("is_hint_anchor"):
        return True
    if not hint_kws:
        return False
    name_n = (place.get("name", "") or "").replace(" ", "")
    if not name_n:
        return False
    return any(name_n == h.replace(" ", "") for h in hint_kws if h)


# ─── shortlist 선별 ───
def select_shortlist(
    scored:        list[dict],
    route_type:    str = "endpoint",
    travel_days:   int = 1,
    start_lat:     float = None,
    start_lng:     float = None,
    end_lat:       float = None,
    end_lng:       float = None,
    hint_keywords: list[str] = None,
) -> list[dict]:

    hint_kws = hint_keywords or []

    if route_type == "only":
        quotas = ONLY_SHORTLIST_QUOTA.get(travel_days, ONLY_SHORTLIST_QUOTA[1])
    elif route_type == "only_day":
        quotas = ONLY_DAY_SHORTLIST_QUOTA.get(travel_days, ONLY_DAY_SHORTLIST_QUOTA[1])
    else:
        quotas = DAY_SHORTLIST_QUOTA

    target_count = quotas["total"]

    # ── 힌트 앵커 먼저 무조건 확보 (quota 계산에서 제외) *(v3.1 신규)* ──
    hint_items  = [item for item in scored if _is_hint_protected(item["place"], hint_kws)]
    hint_ids    = {id(item) for item in hint_items}
    rest_scored = [item for item in scored if id(item) not in hint_ids]

    # 힌트 앵커가 속한 그룹만큼 해당 그룹 quota 차감 (0 밑으로는 안 내려감)
    hint_group_count = {"CE7": 0, "FD6": 0, "other": 0}
    for item in hint_items:
        code = item["place"].get("category_group_code", "") or ""
        group = code if code in ("CE7", "FD6") else "other"
        hint_group_count[group] += 1

    # category_group_code 기준 분류 (점수순 유지, 힌트 제외한 나머지 대상)
    groups: dict[str, list] = {"CE7": [], "FD6": [], "other": []}
    for item in rest_scored:
        code = item["place"].get("category_group_code", "") or ""
        if code == "CE7":
            groups["CE7"].append(item)
        elif code == "FD6":
            groups["FD6"].append(item)
        else:
            groups["other"].append(item)

    # quota만큼 상위 N개 선별 (힌트로 이미 채워진 만큼 quota 차감)
    shortlist = list(hint_items)
    for group_name in ["CE7", "FD6", "other"]:
        limit = max(0, quotas.get(group_name, 0) - hint_group_count[group_name])
        shortlist.extend(groups[group_name][:limit])

    # 부족분 점수순으로 보충 (힌트 포함으로 target_count를 이미 넘겼으면 스킵)
    if len(shortlist) < target_count:
        already_in = {id(item) for item in shortlist}
        for item in scored:
            if id(item) not in already_in:
                shortlist.append(item)
                if len(shortlist) >= target_count:
                    break

    shortlist.sort(key=lambda x: x["total_score"], reverse=True)

    # *(v3.1)* 힌트 앵커는 target_count 컷에서도 예외 — 힌트가 많아서
    # target_count를 넘기더라도 힌트는 자르지 않고, 나머지 자리만 채움
    if len(shortlist) <= target_count:
        return shortlist

    kept_hint  = [item for item in shortlist if id(item) in hint_ids]
    kept_other = [item for item in shortlist if id(item) not in hint_ids]
    slot_left  = max(0, target_count - len(kept_hint))
    final      = kept_hint + kept_other[:slot_left]
    final.sort(key=lambda x: x["total_score"], reverse=True)
    return final