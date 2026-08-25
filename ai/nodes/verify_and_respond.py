# ─────────────────────────────────────────────────────────────────────
# 7. verify_and_respond
# ─────────────────────────────────────────────────────────────────────
# 상세 정보 검증 + 응답 생성 노드
#
# 흐름 (day별):
#   1. 시간 재계산 — route_build 결과(장소 순서 + 슬롯 간 이동시간)만으로는
#      실제 도착/출발 시각이 없으므로 여기서 처음 계산 (utils/finalize/time_recalc.py)
#      자동차인 경우 주차장 블록도 이 단계에서 삽입
#   2. 구글 Places API로 각 장소 검증 (utils/finalize/google_verify.py)
#      - 정보 없음 → "정보없음"
#      - 방문 시각(도착~출발)이 영업시간과 안 맞음 → "영업 종료" → 대체 탐색
#        (같은 bucket + 가까운 순 + 앞뒤 이동 가능 + 그 후보도 영업 중이어야 채택,
#         후보 풀은 scored_by_day 전체를 day 구분 없이 통합)
#      - 대체 성공 시 시간 재계산 다시 수행 (체류시간이 바뀔 수 있음)
#   3. 대체 후보가 끝내 없으면: 그 장소를 제외하고 generate_route_candidates의
#      day 재생성 로직을 다시 돌려(이 노드가 직접 재호출) 새 동선을 만들고,
#      GPT 재호출 없이 총점 최고 1개를 자동 채택해 1번부터 다시 검증 — day당 1회 한도.
#      롤백도 실패하면 원래 장소를 "영업 종료" 상태로 유지한 채 진행(경고만 남김)
#   4. 응답 생성 (utils/finalize/response_build.py) — day별 blocks(place/walk/taxi/parking)
#      + route_type=endpoint면 start/end 블록 조립
# ─────────────────────────────────────────────────────────────────────

import httpx

from nodes.generate_route_candidates import _build_day_routes
from utils.enrich_score.score_filter import select_day_shortlist
from utils.finalize.google_verify import enrich_with_google, is_open, find_replacement
from utils.finalize.time_recalc import route_to_stops, recompute_timeline, add_parking_stops
from utils.finalize.response_build import build_day_response, build_response

WEEKDAY_KR_TO_IDX = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}


# ─── idx 앞/뒤에서 가장 가까운 "실제 장소"(parking 제외) 좌표 — 대체 후보 이동성 검증용 ───
def _prev_real_coord(stops: list[dict], idx: int) -> tuple | None:
    for s in reversed(stops[:idx]):
        if s["kind"] != "parking":
            return s["place"]["lat"], s["place"]["lng"]
    return None


def _next_real_coord(stops: list[dict], idx: int) -> tuple | None:
    for s in stops[idx + 1:]:
        if s["kind"] != "parking":
            return s["place"]["lat"], s["place"]["lng"]
    return None


# ─── stops 안의 place들을 구글로 검증 + (가능하면) 대체 — 끝내 못 고친 장소 id 집합 반환 ───
async def _verify_and_replace(
    client: httpx.AsyncClient,
    stops: list[dict],
    day_number: int,
    replacement_pool: list[dict],
    global_used_ids: set[str],
    transport: str,
    weekday_idx: int,
    warnings: list[str],
) -> set[str]:
    unresolved: set[str] = set()

    for i, s in enumerate(stops):
        if s["kind"] != "place":
            continue
        stops[i]["place"] = await enrich_with_google(client, s["place"])

    for i, s in enumerate(stops):
        if s["kind"] != "place":
            continue
        place = s["place"]
        open_now = is_open(place.get("_opening_hours"), weekday_idx, s["arrive_at"], s["leave_at"])
        status = place.get("status")
        if status != "정보없음":
            status = "영업 중" if open_now else "영업 종료"
        stops[i]["place"] = {**place, "status": status}

        if open_now:
            continue

        warnings.append(f"day{day_number} {place.get('name')} 영업시간 충돌 → 대체 탐색")
        used_ids = {st["place"]["id"] for st in stops if st["kind"] == "place"} | global_used_ids
        replacement = await find_replacement(
            client, place, s["arrive_at"], s["leave_at"], replacement_pool, used_ids,
            weekday_idx, _prev_real_coord(stops, i), _next_real_coord(stops, i), transport,
        )
        if replacement:
            warnings.append(f"day{day_number} {place.get('name')} → {replacement.get('name')} 교체")
            stops[i]["place"] = replacement
        else:
            warnings.append(f"day{day_number} {place.get('name')} 대체 후보 없음")
            unresolved.add(place["id"])

    return unresolved


# ─── 실패 장소 제외 + generate_route_candidates의 day 재생성 로직 직접 재호출 ───
def _regenerate_day(day_number: int, scored_by_day: dict, day_info_map: dict, ui: dict, excluded_ids: set[str]) -> dict | None:
    day_scored = scored_by_day.get(day_number, [])
    pool = [p for p in day_scored if p["id"] not in excluded_ids]
    shortlist = select_day_shortlist(pool)

    routes, _warnings = _build_day_routes(
        day_number, shortlist, day_info_map.get(day_number, {}),
        ui.get("transport", "walk"), ui.get("route_type", "only"),
    )
    return routes[0] if routes else None  # _build_day_routes가 이미 총점 내림차순 정렬해서 반환


# ─── day 하나: 시간 재계산 → 검증/대체 → (필요 시 1회 롤백) ───
async def _process_day(
    day_number: int,
    route: dict,
    ui: dict,
    scored_by_day: dict,
    day_info_map: dict,
    global_used_ids: set[str],
    replacement_pool: list[dict],
    client: httpx.AsyncClient,
) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    transport   = ui.get("transport", "walk")
    start_time  = ui.get("start_time", "11:00")
    weekday_idx = WEEKDAY_KR_TO_IDX.get(ui.get("travel_weekday"), 0)

    rollback_used = False
    excluded_for_day: set[str] = set()
    current_route = route
    stops: list[dict] = []

    for attempt in range(2):
        stops = route_to_stops(current_route)
        if transport == "car":
            stops = await add_parking_stops(stops, client)
        stops = recompute_timeline(stops, start_time, transport)

        unresolved = await _verify_and_replace(
            client, stops, day_number, replacement_pool, global_used_ids, transport, weekday_idx, warnings,
        )
        stops = recompute_timeline(stops, start_time, transport)  # 대체로 체류시간이 바뀌었을 수 있어 재계산

        if not unresolved:
            break

        if rollback_used:
            warnings.append(f"day{day_number} 대체 불가 장소 {unresolved} — 롤백 1회 소진, 원래 장소 유지하고 진행")
            break

        warnings.append(f"day{day_number} 대체 불가 장소 {unresolved} 제외 → 동선 재생성 롤백 시도")
        excluded_for_day |= unresolved
        rollback_used = True

        new_route = _regenerate_day(day_number, scored_by_day, day_info_map, ui, excluded_for_day)
        if new_route is None:
            warnings.append(f"day{day_number} 롤백 재생성 실패 → 원래 장소 유지하고 진행")
            break
        current_route = new_route

    return stops, warnings


# ─── [노드] 상세 정보 검증 + 응답 생성 ───
async def verify_and_respond(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []

    final_itineraries = state.get("final_itineraries") or {}
    scored_by_day      = state.get("scored_by_day") or {}
    days_info          = ui.get("days_info") or []
    day_info_map       = {d["day_number"]: d for d in days_info}

    if not final_itineraries:
        return {
            "response":  {},
            "warnings":  warnings + ["final_itineraries 없음 — select_itinerary 점검 필요"],
            "step":      "respond_failed",
        }

    # 대체 후보 풀 + day 간 중복 방지용 — day 구분 없이 전체 scored_by_day 통합
    replacement_pool = [p for day_list in scored_by_day.values() for p in day_list]
    global_used_ids = {p["id"] for route in final_itineraries.values() for p in route["places"]}

    day_responses: dict[int, dict] = {}

    async with httpx.AsyncClient(timeout=15.0) as client:
        for day_number, route in final_itineraries.items():
            stops, day_warnings = await _process_day(
                day_number, route, ui, scored_by_day, day_info_map, global_used_ids, replacement_pool, client,
            )
            global_used_ids.update(s["place"]["id"] for s in stops if s["kind"] == "place")
            day_responses[day_number] = build_day_response(day_number, stops, ui)
            warnings.extend(day_warnings)

    response = build_response(day_responses, ui)

    return {
        "response": response,
        "warnings": warnings,
        "step":     "done",
    }