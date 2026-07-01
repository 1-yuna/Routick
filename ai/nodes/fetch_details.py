# ─────────────────────────────────────────────────────────────────────
# fetch_details
# ─────────────────────────────────────────────────────────────────────
# 3-8. 최종 일정 기반 정보 보충
#
# 흐름:
#   1. 구글 Places API 호출
#      장소명으로 place_id 조회 → 상세 정보(photos, opening_hours) 조회
#      (최종 선택된 day별 1개 동선, 일반 장소만 대상 — start/end/parking 제외)
#   2. 카카오 Directions API로 이동시간 재계산 (transport=car인 경우만)
#      선택된 최종 동선의 장소 간(주차장 포함) 실제 도로 기반 이동시간 계산
#      → arrive_at, leave_at, travel_to_next_minutes 갱신
#   3. 영업시간 충돌 검증 + 대체 로직
#      각 장소의 도착~출발 시간이 영업시간(요일+시간대, 브레이크타임 포함)과
#      겹치는지 확인. status 필드도 "현재 시점"이 아니라 이 검증 결과로 확정
#      충돌 시 3-3(1차 필터링, day당 50개) 결과를 day 구분 없이 통합한 풀에서
#      대체 후보를 탐색. food는 food끼리만 대체하고, 그 외(activity/cafe/browse/pop)는
#      슬롯 구조상 서로 호환되므로 네 bucket 전체를 대상으로 폭넓게 탐색해
#      5가지 조건을 만족하면 교체 (shortlist 보강 정보가 있으면 우선 사용)
#      대체 적용 후에는 카카오 Directions로 최종 정밀 재계산 수행
#   4. 저녁 food(동선상 마지막 food) 종료 시점이 21:00을 넘기면,
#      그 이후 일정(activity 등)을 모두 잘라내고 바로 도착지(end)로 연결
#   5. 각 블록의 다음 구간 실제 이동수단(travel_mode: 도보/자동차) 부여
#      - 단순히 앞뒤 블록 타입만으로 판단하면 틀릴 수 있어, 차량 보유 상태를
#        동선 순서대로 누적 추적(has_car)하여 정확한 구간별 이동수단 결정
#      - 주차장 도착 시 하차(이후 도보) → 새 주차장으로 이동하는 구간만 차량
# ─────────────────────────────────────────────────────────────────────

import os
import httpx
from datetime import datetime, timedelta

from nodes.generate_candidates import classify_bucket
from nodes.plan_itinerary import search_parking

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
KAKAO_API_KEY  = os.getenv("KAKAO_REST_API_KEY")

GOOGLE_FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
GOOGLE_DETAILS_URL    = "https://maps.googleapis.com/maps/api/place/details/json"
KAKAO_DIRECTIONS_URL  = "https://apis-navi.kakaomobility.com/v1/directions"

TRAVEL_TIME_LIMIT = {"도보": 20, "자동차": 30}

# 요일 인덱스(0=월) → 구글 opening_hours periods의 day(0=일)로 변환
WEEKDAY_TO_GOOGLE_DAY = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}


def to_dt(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── 1. 구글 Places API ─────────────────────────────────────────────

async def _find_place_id(client: httpx.AsyncClient, name: str, lat: float, lng: float) -> str | None:
    try:
        resp = await client.get(
            GOOGLE_FIND_PLACE_URL,
            params={
                "input": name,
                "inputtype": "textquery",
                "locationbias": f"point:{lat},{lng}",
                "fields": "place_id",
                "key": GOOGLE_API_KEY,
            },
        )
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        return candidates[0]["place_id"] if candidates else None
    except Exception:
        return None


async def _fetch_place_details(client: httpx.AsyncClient, google_place_id: str) -> dict:
    try:
        resp = await client.get(
            GOOGLE_DETAILS_URL,
            params={
                "place_id": google_place_id,
                "fields": "photos,opening_hours",
                "key": GOOGLE_API_KEY,
            },
        )
        resp.raise_for_status()
        result = resp.json().get("result", {})

        photo_url = None
        photos = result.get("photos") or []
        if photos:
            photo_ref = photos[0].get("photo_reference")
            if photo_ref:
                photo_url = (
                    "https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=800&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
                )

        return {
            "src":           photo_url,
            "opening_hours": result.get("opening_hours"),
        }
    except Exception:
        return {}


async def _enrich_with_google(client: httpx.AsyncClient, place: dict) -> dict:
    name = place.get("name", "")
    lat  = place.get("lat", 0)
    lng  = place.get("lng", 0)

    google_place_id = await _find_place_id(client, name, lat, lng)
    if not google_place_id:
        return {**place, "status": "영업 정보 없음"}

    details = await _fetch_place_details(client, google_place_id)
    opening_hours = details.get("opening_hours")

    return {
        **place,
        "src":            details.get("src"),
        "status":         "영업 정보 없음",  # 임시값. 도착시간 확정 후 _set_status로 갱신
        "_opening_hours": opening_hours,  # 내부 검증용, 응답에는 미포함
    }


# ─── 2. 카카오 Directions API ───────────────────────────────────────

async def _kakao_directions(client: httpx.AsyncClient, lat1, lng1, lat2, lng2) -> int | None:
    """두 좌표 간 자동차 이동시간(분)을 카카오 Directions API로 조회. 실패 시 None."""
    try:
        resp = await client.get(
            KAKAO_DIRECTIONS_URL,
            params={
                "origin": f"{lng1},{lat1}",
                "destination": f"{lng2},{lat2}",
                "priority": "RECOMMEND",
            },
            headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"},
        )
        resp.raise_for_status()
        routes = resp.json().get("routes", [])
        if not routes or routes[0].get("result_code") != 0:
            return None
        duration_sec = routes[0]["summary"]["duration"]
        return max(1, round(duration_sec / 60))
    except Exception:
        return None


async def _recalculate_travel_times(client: httpx.AsyncClient, itinerary: list[dict]) -> list[dict]:
    """카카오 Directions API로 실제 도로 기반 이동시간을 재계산해 시간표 갱신.
    parking 블록은 체류시간이 없으므로(거쳐가는 지점) 일반 장소와 다르게 처리한다."""
    if not itinerary:
        return itinerary

    result = [dict(item) for item in itinerary]

    # 첫 블록(start) 기준 시간 유지, 이후 순서대로 재계산
    current_time = None
    for i, item in enumerate(result):
        place  = item["place"]
        bucket = place.get("bucket", "")

        if bucket == "start":
            current_time = to_dt(item.get("leave_at", "09:00"))
            continue

        if current_time is None:
            current_time = to_dt(item.get("arrive_at") or "09:00")

        prev_place = result[i - 1]["place"] if i > 0 else None
        if prev_place and prev_place.get("lat") is not None:
            travel_min = await _kakao_directions(
                client,
                prev_place["lat"], prev_place["lng"],
                place["lat"], place["lng"],
            )
            if travel_min is not None:
                current_time = current_time + timedelta(minutes=travel_min)
                if i > 0:
                    result[i - 1]["travel_to_next_minutes"] = travel_min

        if bucket == "end":
            item["arrive_at"] = to_str(current_time)
            continue

        if bucket == "parking":
            # 주차장은 체류시간이 없는 경유 지점.
            if item.get("arrive_at") is None and item.get("leave_at") is None:
                # 연속 주차장의 두 번째 블록(새 주차장): 시간 미표시 유지
                continue

            # 연속 주차장인지 확인 (다음 블록도 parking이면 이전 주차장 복귀 블록)
            next_item = result[i + 1] if i + 1 < len(result) else None
            is_chained = bool(next_item and next_item["place"].get("bucket") == "parking")

            item["arrive_at"] = to_str(current_time)

            if is_chained:
                # 이전 주차장 → 새 주차장까지 실제 자동차 이동시간을 카카오 Directions로 재계산
                next_place = next_item["place"]
                car_min = await _kakao_directions(
                    client, place["lat"], place["lng"], next_place["lat"], next_place["lng"]
                )
                if car_min is None:
                    car_min = item.get("exit_transport", {}).get("minutes", 1)
                leave_time = current_time + timedelta(minutes=car_min)
                item["leave_at"] = to_str(leave_time)
                item["exit_transport"] = {"mode": "car", "minutes": car_min}
                current_time = leave_time
            else:
                item["leave_at"] = to_str(current_time)
            continue

        # 체류시간 유지 (기존 arrive~leave 간격)
        try:
            old_arrive = to_dt(item["arrive_at"])
            old_leave  = to_dt(item["leave_at"])
            stay = int((old_leave - old_arrive).total_seconds() / 60)
        except Exception:
            stay = 60

        item["arrive_at"] = to_str(current_time)
        item["leave_at"]  = to_str(current_time + timedelta(minutes=stay))
        current_time = current_time + timedelta(minutes=stay)

    return result


# ─── 3. 영업시간 충돌 검증 + 대체 로직 ──────────────────────────────

def _parse_weekday_text(text: str, arrive_at: str, leave_at: str) -> bool:
    """weekday_text 한 줄을 파싱해서 영업 중 여부 판단.
    예) "Monday: Open 24 hours" / "Tuesday: 12:00 AM – 10:00 PM" / "Wednesday: Closed"
    """
    import re
    if not text:
        return False
    lower = text.lower()
    if "open 24 hours" in lower:
        return True
    if "closed" in lower:
        return False

    # "Day: HH:MM AM – HH:MM AM" 형태에서 시간 범위 추출
    match = re.search(r":\s*(.+)", text)
    if not match:
        return False
    time_part = match.group(1).strip()
    parts = re.split(r"[–\-]", time_part)
    if len(parts) != 2:
        return False
    try:
        open_t  = datetime.strptime(parts[0].strip(), "%I:%M %p")
        close_t = datetime.strptime(parts[1].strip(), "%I:%M %p")
        open_min  = open_t.hour * 60 + open_t.minute
        close_min = close_t.hour * 60 + close_t.minute
        arrive_min = to_dt(arrive_at).hour * 60 + to_dt(arrive_at).minute
        leave_min  = to_dt(leave_at).hour * 60 + to_dt(leave_at).minute
        if close_min == 0:          # 자정 = 다음날 00:00
            close_min = 24 * 60
        if close_min < open_min:    # 새벽으로 넘어가는 케이스
            close_min += 24 * 60
        return open_min <= arrive_min and leave_min <= close_min
    except Exception:
        return False


def _is_open(opening_hours: dict | None, weekday: int, arrive_at: str, leave_at: str) -> bool:
    """opening_hours.periods 기준으로 도착~출발 시간이 영업시간 내인지 확인.
    정보가 없으면 충돌 없는 것으로 간주(보수적으로 통과)."""
    if not opening_hours:
        return True
    periods = opening_hours.get("periods")
    if not periods:
        return True

    # 구글은 24/7 영업 장소를 open.day=0, open.time="0000", close 없음인
    # 단일 period로 반환함 → 요일 무관하게 항상 영업 중으로 처리
    if (len(periods) == 1
            and periods[0].get("open", {}).get("day") == 0
            and periods[0].get("open", {}).get("time") == "0000"
            and not periods[0].get("close")):
        return True

    google_day = WEEKDAY_TO_GOOGLE_DAY.get(weekday)
    arrive_min = to_dt(arrive_at).hour * 60 + to_dt(arrive_at).minute
    leave_min  = to_dt(leave_at).hour * 60 + to_dt(leave_at).minute

    for period in periods:
        open_info  = period.get("open", {})
        close_info = period.get("close")
        if open_info.get("day") != google_day:
            continue
        open_min = int(open_info.get("time", "0000")[:2]) * 60 + int(open_info.get("time", "0000")[2:])
        if close_info:
            close_time = close_info.get("time", "2359")
            close_min  = int(close_time[:2]) * 60 + int(close_time[2:])
            # close.day가 open.day와 다르면 다음날로 넘어가는 영업 (예: 08:30~다음날 02:00)
            # → close_min에 24*60을 더해 연속 시간으로 처리
            if close_info.get("day") != open_info.get("day"):
                close_min += 24 * 60
        else:
            close_min = 24 * 60  # 24시간 영업

        if open_min <= arrive_min and leave_min <= close_min:
            return True

    # periods에서 해당 요일 매칭 없음 → weekday_text로 fallback
    # (구글 데이터 누락/불일치 케이스 대응)
    weekday_text_list = opening_hours.get("weekday_text", [])
    if len(weekday_text_list) == 7:
        return _parse_weekday_text(weekday_text_list[weekday], arrive_at, leave_at)

    return False


def _haversine(lat1, lng1, lat2, lng2):
    import math
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def _distance_to_minutes(dist_km, transport_kr):
    speed = {"도보": 4, "자동차": 30}.get(transport_kr, 4)
    return max(1, round((dist_km / speed) * 60))


def _segments_intersect(p1, p2, p3, p4):
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    d1, d2 = cross(p3, p4, p1), cross(p3, p4, p2)
    d3, d4 = cross(p1, p2, p3), cross(p1, p2, p4)
    return ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0))


def _causes_intersection(itinerary: list[dict], idx: int, new_place: dict) -> bool:
    """itinerary[idx]를 new_place로 교체했을 때, 그 앞뒤 구간이 나머지 구간과 교차하는지 확인."""
    coords = [(item["place"]["lat"], item["place"]["lng"]) for item in itinerary]
    coords[idx] = (new_place["lat"], new_place["lng"])

    new_segments = []
    if idx > 0:
        new_segments.append((idx - 1, idx))
    if idx < len(coords) - 1:
        new_segments.append((idx, idx + 1))

    for seg_a, seg_b in new_segments:
        p1, p2 = coords[seg_a], coords[seg_b]
        for i in range(len(coords) - 1):
            if i in (seg_a,) or (i + 1 == seg_b and i == seg_a):
                continue
            if abs(i - seg_a) <= 1:
                continue
            p3, p4 = coords[i], coords[i + 1]
            if _segments_intersect(p1, p2, p3, p4):
                return True
    return False


def _assign_travel_mode(itinerary: list[dict], is_car_day: bool) -> list[dict]:
    """각 블록의 다음 구간 이동수단(travel_mode)을 결정해 부여한다.
    단순히 앞뒤 블록 타입만 보면 틀릴 수 있어, 차량 보유 상태(has_car)를
    동선 순서대로 누적 추적하며 판단한다.
    - 자동차 일정(start)은 차를 가진 상태로 출발
    - parking 도착 시 하차 → 이후 도보 상태로 전환
    - 새 parking으로 이동(주차장 간 이동)하는 구간만 다시 차량 탑승
    - 도보 일정은 항상 도보"""
    result   = [dict(item) for item in itinerary]
    has_car  = is_car_day

    i = 0
    while i < len(result):
        item   = result[i]
        bucket = item["place"].get("bucket", "")

        if bucket == "end":
            i += 1
            continue

        if bucket == "parking":
            has_car = False  # 주차장 도착 시 하차

            next_item = result[i + 1] if i + 1 < len(result) else None
            if next_item and next_item["place"].get("bucket") == "parking":
                # 연속 주차장(이전 주차장 복귀 → 새 주차장): 이 구간만 차량 이동
                result[i]["travel_mode"] = "자동차"
                has_car = True
                i += 1
                continue
            else:
                result[i]["travel_mode"] = "도보"
                i += 1
                continue

        result[i]["travel_mode"] = "자동차" if has_car else "도보"
        has_car = False  # 일반 장소 이후에는 다시 도보 (다음이 parking이면 위에서 갱신됨)
        i += 1

    return result


async def _cutoff_after_evening_food(
    itinerary: list[dict],
    transport_kr: str = "도보",
    cutoff_time: str = "21:00",
) -> list[dict]:
    """저녁 food(동선상 마지막 food) 종료 시점이 cutoff_time을 넘기면,
    그 이후의 일반 장소(activity/cafe/browse/pop 등)를 모두 잘라내고
    end 블록만 이어붙인다. start/parking 블록은 그대로 유지.
    transport=자동차인 경우 단순 도보 직결이 아니라, 마지막 food 이전에
    이미 확보된 주차장이 있으면 그 주차장을 복귀 후 end 근처 새 주차장을
    검색해 자동차로 이동하도록 처리한다."""
    food_indices = [
        i for i, item in enumerate(itinerary)
        if item["place"].get("bucket") == "food"
    ]
    if not food_indices:
        return itinerary

    last_food_idx = food_indices[-1]
    last_food_leave = itinerary[last_food_idx].get("leave_at")
    if not last_food_leave or to_dt(last_food_leave) < to_dt(cutoff_time):
        return itinerary  # 21시 이전에 끝났으면 컷오프 불필요

    # 마지막 food 이전(컷오프되지 않는 구간)에서 가장 마지막으로 등장한 주차장을
    # "현재 보유 중인 주차 거점"으로 간주
    current_parking = None
    for item in itinerary[: last_food_idx + 1]:
        if item["place"].get("bucket") == "parking":
            current_parking = item["place"]

    # 마지막 food 이후의 일반 장소/주차장 블록을 모두 제거하고, end 블록만 유지
    result = itinerary[: last_food_idx + 1]
    end_block = next(
        (item for item in itinerary[last_food_idx + 1:] if item["place"].get("bucket") == "end"),
        None
    )

    if not end_block:
        return result

    last_place = itinerary[last_food_idx]["place"]
    end_place  = end_block["place"]
    is_car = transport_kr == "자동차"

    if is_car and current_parking is not None and current_parking.get("lat") is not None:
        dist_to_end = _haversine(current_parking["lat"], current_parking["lng"],
                                  end_place["lat"], end_place["lng"])

        if dist_to_end > 1.0:
            # 보유 주차장에서 end까지 멀면, food → 주차장 복귀(도보) → end 근처 새 주차장(자동차) → end(도보)
            walk_back = _distance_to_minutes(
                _haversine(last_place["lat"], last_place["lng"],
                           current_parking["lat"], current_parking["lng"]),
                "도보"
            )
            park_back_arrive = to_str(to_dt(last_food_leave) + timedelta(minutes=walk_back))

            new_parking = await search_parking(end_place["lat"], end_place["lng"])

            if new_parking:
                car_min = _distance_to_minutes(
                    _haversine(current_parking["lat"], current_parking["lng"],
                               new_parking["lat"], new_parking["lng"]),
                    "자동차"
                )
                new_park_leave = to_str(to_dt(park_back_arrive) + timedelta(minutes=car_min + 1))
                walk_to_end = _distance_to_minutes(
                    _haversine(new_parking["lat"], new_parking["lng"],
                               end_place["lat"], end_place["lng"]),
                    "도보"
                )

                result[last_food_idx]["travel_to_next_minutes"] = walk_back
                result.append({
                    "type":            "parking",
                    "place":           {**current_parking, "bucket": "parking"},
                    "arrive_at":       park_back_arrive,
                    "leave_at":        new_park_leave,
                    "enter_transport": {"mode": "walk", "minutes": walk_back},
                    "exit_transport":  {"mode": "car",  "minutes": car_min},
                    "travel_to_next_minutes": car_min,
                })
                result.append({
                    "type":            "parking",
                    "place":           {**new_parking, "bucket": "parking"},
                    "arrive_at":       None,
                    "leave_at":        None,
                    "enter_transport": {"mode": "car",  "minutes": car_min},
                    "exit_transport":  {"mode": "walk", "minutes": walk_to_end},
                    "travel_to_next_minutes": walk_to_end,
                })
                end_arrive = to_str(to_dt(new_park_leave) + timedelta(minutes=walk_to_end))
                result.append({**end_block, "arrive_at": end_arrive})
                return result

        # 가깝거나 새 주차장을 못 찾았으면 그대로 도보로 연결
        walk_min = _distance_to_minutes(dist_to_end, "도보")
        new_arrive = to_str(to_dt(last_food_leave) + timedelta(minutes=walk_min))
        result.append({**end_block, "arrive_at": new_arrive})
        result[last_food_idx]["travel_to_next_minutes"] = walk_min
    else:
        # 도보 일정이거나 주차장 정보가 없으면 기존처럼 직선거리 기반 도보로 연결
        dist = _haversine(last_place["lat"], last_place["lng"], end_place["lat"], end_place["lng"])
        walk_min = _distance_to_minutes(dist, "도보")
        new_arrive = to_str(to_dt(last_food_leave) + timedelta(minutes=walk_min))
        result.append({**end_block, "arrive_at": new_arrive})
        result[last_food_idx]["travel_to_next_minutes"] = walk_min

    return result


def _recalculate_stay_chain(itinerary: list[dict], from_idx: int) -> list[dict]:
    """from_idx부터 끝까지, 각 장소의 체류시간(기존 arrive~leave 간격)을 유지한 채
    직선거리 기반 이동시간으로 시간표를 다시 이어붙인다.
    (교체 후보 검증용 — 정밀한 재계산은 이후 카카오 Directions 재실행에서 처리)"""
    result = [dict(x) for x in itinerary]
    transport_kr_local = "도보"  # 보수적으로 도보 속도 기준 (가장 느린 케이스로 안전하게 검증)

    if from_idx == 0:
        current_time = to_dt(result[0].get("arrive_at") or "09:00")
    else:
        current_time = to_dt(result[from_idx - 1].get("leave_at") or "09:00")

    prev_place = result[from_idx - 1]["place"] if from_idx > 0 else None

    for i in range(from_idx, len(result)):
        item   = result[i]
        place  = item["place"]
        bucket = place.get("bucket", "")

        if bucket == "start":
            current_time = to_dt(item.get("leave_at") or "09:00")
            prev_place = place
            continue

        if prev_place is not None:
            dist = _haversine(prev_place["lat"], prev_place["lng"], place["lat"], place["lng"])
            travel_min = _distance_to_minutes(dist, transport_kr_local)
            current_time = current_time + timedelta(minutes=travel_min)
            if i > 0:
                result[i - 1]["travel_to_next_minutes"] = travel_min

        if bucket == "end":
            item["arrive_at"] = to_str(current_time)
            prev_place = place
            continue

        try:
            old_arrive = to_dt(item["arrive_at"])
            old_leave  = to_dt(item["leave_at"])
            stay = int((old_leave - old_arrive).total_seconds() / 60)
        except Exception:
            stay = 60

        item["arrive_at"] = to_str(current_time)
        item["leave_at"]  = to_str(current_time + timedelta(minutes=stay))
        current_time = current_time + timedelta(minutes=stay)
        prev_place = place

    return result


async def _find_replacement(
    itinerary: list[dict],
    idx: int,
    all_shortlist: list[dict],
    transport_kr: str,
    travel_weekday: int,
    used_place_ids: set[str],
    google_client: httpx.AsyncClient,
) -> dict | None:
    """충돌난 장소(idx)에 대해 조건을 만족하는 대체 후보를 탐색.
    day 구분 없이 전체 shortlist에서 대체 후보를 찾는다.
    food는 food끼리만 대체하고, 그 외(activity/cafe/browse/pop)는 서로 자유롭게
    대체 가능하도록 범위를 넓혀 탐색한다 (슬롯 구조상 이 네 bucket은 상호 호환됨)."""
    target = itinerary[idx]["place"]
    target_bucket = target.get("bucket", "")
    if target_bucket == "food":
        target_buckets = ["food"]
    else:
        target_buckets = ["activity", "cafe", "browse", "pop"]
    prev_place = itinerary[idx - 1]["place"] if idx > 0 else None
    next_place = itinerary[idx + 1]["place"] if idx < len(itinerary) - 1 else None
    travel_limit = TRAVEL_TIME_LIMIT.get(transport_kr, 20)

    arrive_at = itinerary[idx]["arrive_at"]
    leave_at  = itinerary[idx]["leave_at"]

    # 대상 bucket 범위 내, 아직 동선에 쓰이지 않은 전체 shortlist 후보를
    # target과 가까운 순으로 정렬 (day 구분 없이 전체에서 탐색)
    candidates = [
        s["place"] for s in all_shortlist
        if s["place"].get("bucket") in target_buckets
        and s["place"]["id"] not in used_place_ids
        and s["place"]["id"] != target["id"]
    ]
    candidates.sort(key=lambda c: _haversine(target["lat"], target["lng"], c["lat"], c["lng"]))

    for c in candidates:
        # ① 해당 시간대 영업 중 (구글 정보 보강 후 확인)
        c_enriched = await _enrich_with_google(google_client, c)
        if not _is_open(c_enriched.get("_opening_hours"), travel_weekday, arrive_at, leave_at):
            continue

        # ② prev→C, C→next 이동시간이 초과 기준 이내
        ok = True
        if prev_place:
            d1 = _haversine(prev_place["lat"], prev_place["lng"], c["lat"], c["lng"])
            t1 = _distance_to_minutes(d1, transport_kr)
            if t1 > travel_limit:
                ok = False
        if ok and next_place:
            d2 = _haversine(c["lat"], c["lng"], next_place["lat"], next_place["lng"])
            t2 = _distance_to_minutes(d2, transport_kr)
            if t2 > travel_limit:
                ok = False
        if not ok:
            continue

        # ③ prev→C→next 총 이동시간이 기존 prev→P→next 대비 크게 늘지 않음 (150% 이내)
        if prev_place and next_place:
            old_d = (_haversine(prev_place["lat"], prev_place["lng"], target["lat"], target["lng"])
                      + _haversine(target["lat"], target["lng"], next_place["lat"], next_place["lng"]))
            new_d = (_haversine(prev_place["lat"], prev_place["lng"], c["lat"], c["lng"])
                      + _haversine(c["lat"], c["lng"], next_place["lat"], next_place["lng"]))
            if old_d > 0 and new_d > old_d * 1.5:
                continue

        # ④ 경로 교차 없음
        if _causes_intersection(itinerary, idx, c):
            continue

        # ⑤ 이후 시간표가 endTime을 넘지 않는지는 호출부에서 재계산 후 검증
        return {**c_enriched, "slot_buckets": target_buckets}

    return None


# ─── [노드] 정보 보충 ────────────────────────────────────────────────

async def fetch_details(state: dict) -> dict:
    ui = state["user_input"]
    final_itineraries: dict[int, list[dict]] = state.get("final_itineraries", {})
    shortlist_by_day = state.get("shortlist_by_day", {})
    filtered_by_day  = state.get("filtered_by_day", {})  # 3-3 1차 필터링 결과 (대체 후보 풀)
    warnings: list[str] = []

    transport_kr   = ui.get("transport_kr", "도보")
    travel_weekday_kr = ui.get("travel_weekday")
    end_time       = ui.get("end_time", "22:00")

    weekday_map_kr_to_idx = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
    travel_weekday = weekday_map_kr_to_idx.get(travel_weekday_kr, 0)

    if not final_itineraries:
        return {
            "final_itineraries": {},
            "warnings": ["final_itineraries 비어있음"],
            "step": "failed",
        }

    # 대체 후보 풀: 3-3(1차 필터링, day당 50개) 결과 기준 — day 구분 없이 전체 통합
    # bucket이 아직 없으므로 classify_bucket으로 그 자리에서 분류
    all_shortlist: list[dict] = []
    seen_ids: set[str] = set()
    for day_filtered in filtered_by_day.values():
        for p in day_filtered:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                p_with_bucket = {**p, "bucket": classify_bucket(p)}
                all_shortlist.append({"place": p_with_bucket, "total_score": 0})

    # shortlist(2차 필터 보강 데이터: atmosphere/best_for/place_tags/summary)가 있는 장소는
    # 더 풍부한 정보로 덮어써서 추천 이유 생성 등에 활용
    for day_sl in shortlist_by_day.values():
        for s in day_sl:
            for i, existing in enumerate(all_shortlist):
                if existing["place"]["id"] == s["place"]["id"]:
                    all_shortlist[i] = s
                    break

    result_itineraries: dict[int, list[dict]] = {}

    async with httpx.AsyncClient(timeout=15.0) as google_client, \
               httpx.AsyncClient(timeout=15.0) as kakao_client:

        for day_number, itinerary in final_itineraries.items():
            # 1. 구글 Places로 일반 장소만 정보 보강 (start/end/parking 제외)
            enriched = []
            for item in itinerary:
                place = item["place"]
                bucket = place.get("bucket", "")
                if bucket in ("start", "end", "parking"):
                    enriched.append(item)
                    continue
                new_place = await _enrich_with_google(google_client, place)
                enriched.append({**item, "place": new_place})

            # 2. 카카오 Directions로 이동시간 재계산 (자동차만)
            if transport_kr == "자동차":
                enriched = await _recalculate_travel_times(kakao_client, enriched)

            # 3. 영업시간 충돌 검증 + 대체 로직 (전체 shortlist 대상)
            used_place_ids = {
                item["place"]["id"] for item in enriched
                if item["place"].get("bucket") not in ("start", "end", "parking")
            }

            for idx, item in enumerate(enriched):
                place = item["place"]
                bucket = place.get("bucket", "")
                if bucket in ("start", "end", "parking"):
                    continue

                is_open = _is_open(
                    place.get("_opening_hours"), travel_weekday,
                    item["arrive_at"], item["leave_at"]
                )
                # status는 "지금 이 순간"이 아니라 여행 날짜의 방문(도착~출발) 시간 기준으로 확정
                enriched[idx]["place"] = {
                    **place,
                    "status": "영업 중" if is_open else "영업 종료",
                }
                if is_open:
                    continue
                place = enriched[idx]["place"]

                warnings.append(f"day{day_number} {place.get('name')} 영업시간 충돌 → 대체 탐색")
                replacement = await _find_replacement(
                    [i for i in enriched],
                    idx, all_shortlist, transport_kr, travel_weekday,
                    used_place_ids, google_client,
                )

                if replacement:
                    replacement = {**replacement, "status": "영업 중"}
                    # ⑤ 교체 후 이후 시간표 재계산 시 endTime을 넘지 않는지 검증
                    trial = [dict(x) for x in enriched]
                    trial[idx] = {**enriched[idx], "place": replacement}
                    trial = _recalculate_stay_chain(trial, idx)

                    last_real = next(
                        (x for x in reversed(trial) if x["place"].get("bucket") not in ("start", "end", "parking")),
                        None
                    )
                    exceeds_end_time = last_real and to_dt(last_real["leave_at"]) > to_dt(end_time)

                    if exceeds_end_time:
                        warnings.append(f"day{day_number} {place.get('name')} 대체 시 endTime 초과 → 원래 장소 유지")
                    else:
                        enriched = trial
                        used_place_ids.discard(place["id"])
                        used_place_ids.add(replacement["id"])
                        warnings.append(f"day{day_number} {place.get('name')} → {replacement.get('name')} 교체")
                else:
                    warnings.append(f"day{day_number} {place.get('name')} 대체 후보 없음 → 원래 장소 유지")

            # 영업시간 대체로 동선이 바뀌었을 수 있으므로 카카오 Directions로 최종 정밀 재계산
            if transport_kr == "자동차":
                enriched = await _recalculate_travel_times(kakao_client, enriched)

            # 저녁 food 이후 21:00을 넘기면 그 뒤 일정을 모두 잘라내고 바로 도착지로 연결
            # (transport=자동차면 보유 주차장 기준으로 주차장 재경유 처리)
            enriched = await _cutoff_after_evening_food(enriched, transport_kr=transport_kr, cutoff_time="21:00")

            # 각 블록의 다음 구간 실제 이동수단(도보/자동차) 부여
            enriched = _assign_travel_mode(enriched, is_car_day=(transport_kr == "자동차"))

            # _opening_hours 내부 필드 제거 (응답에 미포함)
            for item in enriched:
                if "_opening_hours" in item["place"]:
                    item["place"] = {k: v for k, v in item["place"].items() if k != "_opening_hours"}

            result_itineraries[day_number] = enriched

    return {
        "final_itineraries": result_itineraries,
        "warnings":          warnings,
        "step":              "details_fetched",
    }