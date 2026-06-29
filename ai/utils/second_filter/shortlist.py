# ─────────────────────────────────────────────────────────────────────
# shortlist
# ─────────────────────────────────────────────────────────────────────
# scored_candidates → shortlist
#
# 흐름:
#   1. category_group_code 기반으로 분류 (CE7/FD6/나머지)
#   2. route_type / travel_days 기반 quota 정의
#      - 케이스 1 (only): travel_days별 전체 quota (30/50/70/80개)
#      - 케이스 2 (endpoint): day당 고정 30개
#   3. quota만큼 점수순으로 선별
#   4. 부족분은 점수순으로 보충
# ─────────────────────────────────────────────────────────────────────

# ─── 케이스 1 (only): travel_days별 전체 quota ───
ONLY_SHORTLIST_QUOTA = {
    1: {"CE7": 5,  "FD6": 8,  "other": 17, "total": 30},
    2: {"CE7": 8,  "FD6": 13, "other": 29, "total": 50},
    3: {"CE7": 11, "FD6": 18, "other": 41, "total": 70},
    4: {"CE7": 13, "FD6": 21, "other": 46, "total": 80},
}

# ─── 케이스 2 (endpoint): day당 고정 quota ───
DAY_SHORTLIST_QUOTA = {"CE7": 5, "FD6": 8, "other": 17, "total": 30}


# ─── shortlist 선별 ───
def select_shortlist(
    scored:      list[dict],
    route_type:  str = "endpoint",
    travel_days: int = 1,
) -> list[dict]:

    if route_type == "only":
        quotas = ONLY_SHORTLIST_QUOTA.get(travel_days, ONLY_SHORTLIST_QUOTA[1])
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