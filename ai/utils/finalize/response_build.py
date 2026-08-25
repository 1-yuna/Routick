# ─────────────────────────────────────────────────────────────────────
# response_build
# ─────────────────────────────────────────────────────────────────────
# 검증 + 시간 재계산까지 끝난 day별 stops를 최종 응답 JSON으로 변환
#   - blocks 배열: place / walk / taxi / parking 타입 혼합
#   - route_type=endpoint면 day별 start/end 블록 추가
# ─────────────────────────────────────────────────────────────────────


# ─── 원본 입력(ui["days"])에서 day의 출발/도착지 이름·주소 조회 (endpoint 전용) ───
def _raw_day_coord(ui: dict, day_number: int) -> dict:
    for d in ui.get("days") or []:
        if d.get("day_number") == day_number:
            return d
    return {}


# ─── 직전 stop의 travel_to_next를 "이 stop으로 들어오는 이동정보"로 변환 ───
def _incoming_transport(stops: list[dict], idx: int) -> dict | None:
    if idx == 0:
        return None
    prev = stops[idx - 1]
    if "travel_to_next_minutes" not in prev:
        return None
    return {"mode": prev["travel_mode"], "minutes": prev["travel_to_next_minutes"]}


# ─── day 하나의 stops → {start, end, blocks} ───
def build_day_response(day_number: int, stops: list[dict], ui: dict) -> dict:
    route_type = ui.get("route_type", "only")
    day_obj: dict = {"day_number": day_number}

    if route_type == "endpoint":
        raw = _raw_day_coord(ui, day_number)
        start_stop = next((s for s in stops if s["kind"] == "start"), None)
        end_stop   = next((s for s in stops if s["kind"] == "end"), None)

        if start_stop:
            day_obj["start"] = {
                "name":            raw.get("start_name", ""),
                "address":         raw.get("start_address", ""),
                "lat":             start_stop["place"]["lat"],
                "lng":             start_stop["place"]["lng"],
                "place_id":        raw.get("start_place_id", ""),
                "exit_transport":  {"mode": start_stop.get("travel_mode"), "minutes": start_stop.get("travel_to_next_minutes", 0)},
            }
        if end_stop:
            end_idx = stops.index(end_stop)
            day_obj["end"] = {
                "name":            raw.get("end_name", ""),
                "address":         raw.get("end_address", ""),
                "lat":             end_stop["place"]["lat"],
                "lng":             end_stop["place"]["lng"],
                "place_id":        raw.get("end_place_id", ""),
                "enter_transport": _incoming_transport(stops, end_idx),
            }

    blocks = []
    block_order = 1
    place_order = 1

    for i, s in enumerate(stops):
        kind = s["kind"]
        if kind in ("start", "end"):
            continue

        if kind == "parking":
            p = s["place"]
            blocks.append({
                "block_order":     block_order,
                "type":            "parking",
                "bucket":          "parking",
                "place_id":        p.get("id", ""),
                "name":            p.get("name", ""),
                "address":         p.get("address", ""),
                "description":     None,
                "lat":             p.get("lat", 0.0),
                "lng":             p.get("lng", 0.0),
                "arrive_time":     s.get("arrive_at"),
                "leave_time":      s.get("leave_at"),
                "enter_transport": _incoming_transport(stops, i),
                "exit_transport":  {"mode": s.get("travel_mode"), "minutes": s.get("travel_to_next_minutes", 0)} if "travel_to_next_minutes" in s else None,
            })
            block_order += 1
            continue

        # kind == "place"
        p = s["place"]
        blocks.append({
            "block_order":  block_order,
            "type":         "place",
            "bucket":       p.get("bucket", ""),
            "place_order":  place_order,
            "place_id":     p.get("id", ""),
            "name":         p.get("name", ""),
            "address":      p.get("road_address_name") or p.get("address_name", ""),
            "image_url":    p.get("src"),
            "status":       p.get("status", "정보없음"),
            "description":  p.get("summary", ""),
            "lat":          p.get("lat", 0.0),
            "lng":          p.get("lng", 0.0),
            "stay_minutes": s.get("leave_at") and s.get("arrive_at") and _minutes_between(s["arrive_at"], s["leave_at"]),
            "arrive_time":  s.get("arrive_at"),
            "leave_time":   s.get("leave_at"),
        })
        block_order += 1
        place_order += 1

        next_stop = stops[i + 1] if i + 1 < len(stops) else None
        if next_stop and next_stop["kind"] != "parking" and "travel_to_next_minutes" in s:
            seg_type = s.get("travel_mode", "walk")  # walk/taxi/car 실제 값 그대로 (walk로 뭉개지 않음)
            blocks.append({
                "block_order": block_order,
                "type":        seg_type,
                "minutes":     s["travel_to_next_minutes"],
            })
            block_order += 1

    day_obj["blocks"] = blocks
    return day_obj


def _minutes_between(arrive_at: str, leave_at: str) -> int:
    from datetime import datetime
    a = datetime.strptime(arrive_at, "%H:%M")
    l = datetime.strptime(leave_at, "%H:%M")
    return int((l - a).total_seconds() / 60)


# ─── 전체 응답 조립 (meta + day별 응답) ───
def build_response(day_responses: dict[int, dict], ui: dict) -> dict:
    meta = {
        "period":    ui.get("duration_kr", ""),
        "date":      ui.get("travel_date", ""),
        "companion": ui.get("companion_kr", ""),
        "mood":      ui.get("moods_kr") or [],
        "activity":  ui.get("activities_kr") or [],
        "dislike":   ui.get("avoid_activities") or [],
    }

    days_info = ui.get("days_info") or []
    region_by_day = {d["day_number"]: d.get("region_name", "") for d in days_info}
    for day_number, day_obj in day_responses.items():
        day_obj["region"] = region_by_day.get(day_number, "")

    return {
        "transport": ui.get("transport", "walk"),
        "meta":      meta,
        "days":      [day_responses[d] for d in sorted(day_responses.keys())],
    }