# ─────────────────────────────────────────────────────────────────────
# generate_response
# ─────────────────────────────────────────────────────────────────────
# select_itinerary → fetch_details에서 선택된 최종 동선을
# Spring 백엔드 응답 형식으로 변환 (응답 키: snake_case)
#
# 흐름:
#   1. meta, transport 최상위 필드 구성
#   2. day별 region/start_region/end_region 매핑
#   3. route_type=endpoint: start/end 블록 구성
#   4. blocks 배열 구성 (place/walk/parking 타입 혼합)
#      - place 블록 사이에 walk 블록 삽입
#      - parking 블록은 enter/exit_transport 포함
# ─────────────────────────────────────────────────────────────────────

from utils.route.greedy_nn import STAY_MINUTES


# ─── 이동수단 한국어 → 영어 ───
TRANSPORT_MAP = {"도보": "walk", "자동차": "car", "택시": "taxi"}   # *(v3)* taxi 추가


# ─── [노드] 응답 생성 ───
def generate_response(state: dict) -> dict:
    # LangGraph 흐름에서는 fetch_details가 "final_itineraries"(dict[int, list])로 반환하고
    # generate_response는 "selected_itinerary"(list[{day_number, itinerary}])를 기대하므로 여기서 변환
    if "selected_itinerary" in state and state["selected_itinerary"]:
        selected_itinerary = state["selected_itinerary"]
    else:
        final_itineraries = state.get("final_itineraries", {})
        selected_itinerary = [
            {"day_number": day_number, "itinerary": itinerary}
            for day_number, itinerary in final_itineraries.items()
        ]

    ui       = state["user_input"]
    warnings = []

    transport_kr = ui.get("transport_kr", "도보")
    transport    = TRANSPORT_MAP.get(transport_kr, "walk")
    route_type   = ui.get("route_type", "only")
    days_info    = ui.get("days_info") or []

    # ── meta ──────────────────────────────────────────────────────────
    meta = {
        "period":    ui.get("duration_kr", "당일치기"),
        "date":      ui.get("travel_date", ""),
        "companion": ui.get("companion_kr", ""),
        "mood":      ui.get("moods_kr") or [],
        "activity":  ui.get("activities_kr") or [],
        "dislike":   ui.get("avoid_activities") or [],
    }

    # ── region (days 밖, 전체 여행 기준) ────────────────────────────
    if route_type == "only":
        first_day_info = next((d for d in days_info if d.get("day_number") == 1), {})
        region_fields  = {"region": first_day_info.get("region", "")}
    else:
        first_day_info = next((d for d in days_info if d.get("day_number") == 1), {})
        last_day_info  = next((d for d in reversed(days_info)), {})
        region_fields  = {
            "start_region": first_day_info.get("start_region", ""),
            "end_region":   last_day_info.get("end_region", ""),
        }

    days = []

    for day_data in selected_itinerary:
        day_number = day_data["day_number"]
        itinerary  = day_data["itinerary"]

        day_info = next((d for d in days_info if d.get("day_number") == day_number), {})
        day_obj  = {"day_number": day_number}

        # ── start/end/main 분리 ───────────────────────────────────────
        start_item = None
        end_item   = None
        main_items = []

        for item in itinerary:
            bucket = item["place"].get("bucket", "")
            if bucket == "start":
                start_item = item
            elif bucket == "end":
                end_item = item
            else:
                main_items.append(item)

        # ── start 블록 (endpoint만) ───────────────────────────────────
        if route_type == "endpoint" and start_item:
            p = start_item["place"]
            day_obj["start"] = {
                "name":     p.get("name", ""),
                "address":  p.get("address", ""),
                "lat":      p.get("lat", 0.0),
                "lng":      p.get("lng", 0.0),
                "place_id": p.get("id", ""),
                "exit_transport": {
                    # *(v3)* 출발지→첫 장소 구간이 택시 태깅됐으면 taxi로 출력
                    "mode":    TRANSPORT_MAP.get(start_item.get("travel_mode") or transport_kr, transport),
                    "minutes": start_item.get("travel_to_next_minutes", 0),
                },
            }

        # ── end 블록 (endpoint만) ─────────────────────────────────────
        if route_type == "endpoint" and end_item:
            p = end_item["place"]
            # 마지막 일반 장소 → end 이동시간
            last_main    = next((x for x in reversed(main_items)
                                 if x["place"].get("bucket") != "parking"), None)
            enter_minutes = last_main.get("travel_to_next_minutes", 0) if last_main else 0
            enter_mode    = "walk"
            # travel_mode가 있으면 사용
            if last_main:
                enter_mode = TRANSPORT_MAP.get(last_main.get("travel_mode", "도보"), "walk")

            day_obj["end"] = {
                "name":     p.get("name", ""),
                "address":  p.get("address", ""),
                "lat":      p.get("lat", 0.0),
                "lng":      p.get("lng", 0.0),
                "place_id": p.get("id", ""),
                "enter_transport": {
                    "mode":    enter_mode,
                    "minutes": enter_minutes,
                },
            }

        # ── blocks 구성 ───────────────────────────────────────────────
        blocks        = []
        block_order   = 1
        place_order   = 1
        prev_leave_at = start_item.get("leave_at") if start_item else ui.get("start_time", "11:00")

        for i, item in enumerate(main_items):
            place  = item["place"]
            bucket = place.get("bucket", "other")

            # ── parking 블록 ─────────────────────────────────────────
            if bucket == "parking":
                # 연속 주차장 시퀀스의 끝 인덱스 찾기
                j = i
                while j < len(main_items) and main_items[j]["place"].get("bucket") == "parking":
                    j += 1
                last_parking_item = main_items[j - 1]

                # arrive_time: 이전 장소 출발 시간 (이동 시작)
                adjusted_arrive = prev_leave_at

                # leave_time: 마지막 주차장 leave_at + exit_transport.minutes (도보 이동 후 다음 장소 도착)
                last_exit_min = (last_parking_item.get("exit_transport") or {}).get("minutes", 0)
                last_leave    = last_parking_item.get("leave_at")
                if last_leave:
                    from datetime import datetime, timedelta as _td
                    adjusted_leave = (
                            datetime.strptime(last_leave, "%H:%M") + _td(minutes=last_exit_min)
                    ).strftime("%H:%M")
                else:
                    adjusted_leave = None

                parking_block = {
                    "block_order": block_order,
                    "type":        "parking",
                    "bucket":      "parking",
                    "place_id":    place.get("id", ""),
                    "name":        place.get("name", ""),
                    "address":     place.get("road_address_name") or place.get("address", ""),
                    "description": place.get("description"),
                    "lat":         place.get("lat", 0.0),
                    "lng":         place.get("lng", 0.0),
                    "arrive_time": adjusted_arrive,
                    "leave_time":  adjusted_leave,
                }
                if item.get("enter_transport"):
                    parking_block["enter_transport"] = item["enter_transport"]
                elif adjusted_arrive and adjusted_leave:
                    # enter_transport가 None인 경우 (첫 주차장 등) 시간 차로 역산
                    from datetime import datetime as _dt2
                    arrive_min = _dt2.strptime(adjusted_arrive, "%H:%M").hour * 60 + _dt2.strptime(adjusted_arrive, "%H:%M").minute
                    leave_min  = _dt2.strptime(adjusted_leave, "%H:%M").hour * 60 + _dt2.strptime(adjusted_leave, "%H:%M").minute
                    inferred_min = max(1, leave_min - arrive_min - last_exit_min)
                    parking_block["enter_transport"] = {"mode": transport, "minutes": inferred_min}
                if item.get("exit_transport"):
                    parking_block["exit_transport"] = item["exit_transport"]

                blocks.append(parking_block)
                block_order += 1
                # 연속 주차장이면 두 번째도 같은 시간 범위로
                prev_leave_at = adjusted_leave
                continue

            # ── place 블록 ───────────────────────────────────────────
            stay_minutes = STAY_MINUTES.get(bucket, 60)
            blocks.append({
                "block_order":  block_order,
                "type":         "place",
                "bucket":       bucket,
                "place_order":  place_order,
                "place_id":     place.get("id", ""),
                "name":         place.get("name", ""),
                "address":      place.get("road_address_name", ""),
                "image_url":    place.get("src"),
                "status":       place.get("status", ""),
                "description":  item.get("recommendation_reason", ""),
                "lat":          place.get("lat", 0.0),
                "lng":          place.get("lng", 0.0),
                "stay_minutes": stay_minutes,
                "arrive_time":  item.get("arrive_at", ""),
                "leave_time":   item.get("leave_at", ""),
            })
            block_order += 1
            place_order += 1
            prev_leave_at = item.get("leave_at")  # 다음 parking 블록의 arrive_time 기준

            # ── walk/taxi 블록 삽입 조건 ─────────────────────────────
            # 다음 블록이 존재하고 parking이 아닌 경우에만 삽입
            # *(v3)* travel_mode="택시" 구간은 type=taxi로 출력
            # (walk와 동일 필드 구조의 병렬 블록 타입 — parking처럼 별도 type)
            travel_min  = item.get("travel_to_next_minutes", 0)
            next_item   = main_items[i + 1] if i + 1 < len(main_items) else None
            next_bucket = next_item["place"].get("bucket", "") if next_item else ""

            if travel_min > 0 and next_item and next_bucket != "parking":
                seg_type = "taxi" if item.get("travel_mode") == "택시" else "walk"
                blocks.append({
                    "block_order": block_order,
                    "type":        seg_type,
                    "minutes":     travel_min,
                })
                block_order += 1

        # ── parking leave_time = 다음 place arrive_time으로 보정 ───────
        for idx, block in enumerate(blocks):
            if block["type"] == "parking":
                for next_block in blocks[idx + 1:]:
                    if next_block["type"] == "place":
                        block["leave_time"] = next_block["arrive_time"]
                        break
                # arrive_time > leave_time 역전 방지
                # (plan_itinerary에서 start_time 이전으로 계산된 경우)
                if block.get("arrive_time") and block.get("leave_time"):
                    from datetime import datetime as _dt2
                    arr = _dt2.strptime(block["arrive_time"], "%H:%M")
                    lev = _dt2.strptime(block["leave_time"], "%H:%M")
                    if arr > lev:
                        # arrive_time 기준으로 enter+exit 시간 합산해서 leave_time 재계산
                        enter_min = (block.get("enter_transport") or {}).get("minutes", 0)
                        exit_min  = (block.get("exit_transport") or {}).get("minutes", 0)
                        from datetime import timedelta as _td2
                        new_leave = arr + _td2(minutes=enter_min + exit_min)
                        block["leave_time"] = new_leave.strftime("%H:%M")
                        # 다음 place arrive_time도 맞춰서 업데이트
                        for next_block in blocks[idx + 1:]:
                            if next_block["type"] == "place":
                                next_block["arrive_time"] = block["leave_time"]
                                break

        day_obj["blocks"] = blocks
        days.append(day_obj)

    response = {
        "transport": transport,
        "meta":      meta,
        **region_fields,
        "days":      days,
    }

    return {
        "response": response,
        "warnings": warnings,
        "step":     "done",
    }