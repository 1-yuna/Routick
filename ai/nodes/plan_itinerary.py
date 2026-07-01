# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# 점수 기반 day별 상위 5개 추출 + 주차장 추가
#
# 흐름:
#   1. 주차장 거점 정보 추가 (transport=car인 경우만)
#      - 동선 내 장소 순회하며 current_parking 기준으로 주차장 블록 추가
#      - 1km 이내: 기존 주차장 유지
#      - 1km 초과: 이전 주차장 복귀 블록 + 새 주차장 블록 추가
#      - end(도착지) 도착 시에도 동일하게 거리 체크: 현재 주차장에서 end까지
#        1km 초과면 이전 주차장 복귀 → end 근처 새 주차장 검색 → 자동차로 이동 →
#        새 주차장에서 end까지 도보로 연결
#      - 이동시간은 Haversine 기반 추정값 (정확한 재계산은 3-8에서 수행)
#   2. total_score 내림차순 정렬 후 day별 상위 5개 반환
#      유효 동선 1개 이상이면 진행, 없으면 실패 응답
# ─────────────────────────────────────────────────────────────────────

import math
import os
import httpx
from datetime import datetime, timedelta

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

MAX_ITINERARIES_PER_DAY   = 5
PARKING_REUSE_DISTANCE_KM = 1.0
CAR_SPEED_KMH             = 30.0
WALK_SPEED_KMH            = 4.0


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def travel_min(dist_km, speed_kmh):
    return max(1, round((dist_km / speed_kmh) * 60))


def to_dt(t):
    return datetime.strptime(t, "%H:%M")


def to_str(dt):
    return dt.strftime("%H:%M")


async def search_parking(lat, lng, radius_m=500):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                "https://dapi.kakao.com/v2/local/search/category.json",
                headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"},
                params={"category_group_code": "PK6", "x": lng, "y": lat, "radius": radius_m, "size": 1},
            )
            resp.raise_for_status()
            docs = resp.json().get("documents", [])
            if not docs:
                return None
            doc = docs[0]
            return {
                "id":                  doc["id"],
                "name":                doc["place_name"],
                "address":             doc.get("road_address_name") or doc.get("address_name", ""),
                "lat":                 float(doc["y"]),
                "lng":                 float(doc["x"]),
                "category":            doc.get("category_name", ""),
                "category_group_code": "PK6",
                "bucket":              "parking",
                "description":         None,
            }
        except Exception:
            return None


# ─── 동선에 주차장 블록 추가 ───
async def add_parking_to_itinerary(itinerary: list[dict]) -> list[dict]:
    if not itinerary:
        return itinerary

    result          = []
    current_parking = None

    for idx, item in enumerate(itinerary):
        place  = item["place"]
        bucket = place.get("bucket", "")

        # start/end 블록은 주차장 대상에서 제외하되, end는 주차장 경유 시 arrive_at 재계산
        if bucket == "start":
            result.append(item)
            continue
        if bucket == "end":
            end_lat = place.get("lat", 0)
            end_lng = place.get("lng", 0)

            if current_parking is not None:
                dist_to_end = haversine(current_parking["lat"], current_parking["lng"], end_lat, end_lng)

                if dist_to_end > PARKING_REUSE_DISTANCE_KM:
                    # end가 현재 주차장에서 멀면, 마지막 장소 → 주차장 복귀 → end 근처 새 주차장 경유 → end
                    last_place_item = result[-1] if result and result[-1].get("place", {}).get("bucket") not in ("parking",) else None
                    leave_at = (last_place_item or item).get("leave_at") or item.get("arrive_at") or "09:00"
                    last_place = (last_place_item or item)["place"]

                    walk_back_min = travel_min(
                        haversine(last_place["lat"], last_place["lng"],
                                  current_parking["lat"], current_parking["lng"]),
                        WALK_SPEED_KMH
                    )
                    old_park_arrive = to_str(to_dt(leave_at) + timedelta(minutes=walk_back_min))

                    end_parking = await search_parking(end_lat, end_lng)
                    if end_parking:
                        car_min = travel_min(
                            haversine(current_parking["lat"], current_parking["lng"],
                                      end_parking["lat"], end_parking["lng"]),
                            CAR_SPEED_KMH
                        )
                        new_park_arrive = to_str(to_dt(old_park_arrive) + timedelta(minutes=car_min))
                        new_park_leave  = to_str(to_dt(new_park_arrive) + timedelta(minutes=1))

                        walk_to_end = travel_min(
                            haversine(end_parking["lat"], end_parking["lng"], end_lat, end_lng),
                            WALK_SPEED_KMH
                        )

                        # 이전 주차장 복귀 블록
                        result.append({
                            "type":            "parking",
                            "place":           current_parking,
                            "arrive_at":       old_park_arrive,
                            "leave_at":        new_park_leave,
                            "enter_transport": {"mode": "walk", "minutes": walk_back_min},
                            "exit_transport":  {"mode": "car",  "minutes": car_min},
                            "travel_to_next_minutes": car_min,
                        })

                        # end 근처 새 주차장 블록
                        result.append({
                            "type":            "parking",
                            "place":           end_parking,
                            "arrive_at":       None,
                            "leave_at":        None,
                            "enter_transport": {"mode": "car",  "minutes": car_min},
                            "exit_transport":  {"mode": "walk", "minutes": walk_to_end},
                            "travel_to_next_minutes": walk_to_end,
                        })

                        new_end_arrive = to_str(to_dt(new_park_leave) + timedelta(minutes=walk_to_end))
                        item = {**item, "arrive_at": new_end_arrive}
                        result.append(item)
                        continue

            # 1km 이내거나 새 주차장을 못 찾은 경우: 기존처럼 직전 주차장에서 도보로 이동
            if result and result[-1].get("type") == "parking" and result[-1].get("leave_at"):
                # 직전이 새 주차장 블록이면: 주차장 → end까지 도보 이동시간 반영
                last_parking = result[-1]
                walk_to_end = travel_min(
                    haversine(last_parking["place"]["lat"], last_parking["place"]["lng"],
                              end_lat, end_lng),
                    WALK_SPEED_KMH
                )
                new_arrive = to_str(to_dt(last_parking["leave_at"]) + timedelta(minutes=walk_to_end))
                item = {**item, "arrive_at": new_arrive}
            result.append(item)
            continue

        lat = place.get("lat", 0)
        lng = place.get("lng", 0)

        # ── 첫 장소: 진입 전 주차장 검색 ──
        if current_parking is None:
            parking = await search_parking(lat, lng)
            if parking:
                current_parking = parking
                walk_min = travel_min(
                    haversine(parking["lat"], parking["lng"], lat, lng),
                    WALK_SPEED_KMH
                )
                arrive_at = item.get("arrive_at", "09:00")
                park_leave  = to_str(to_dt(arrive_at) - timedelta(minutes=walk_min))
                park_arrive = to_str(to_dt(park_leave) - timedelta(minutes=1))
                result.append({
                    "type":            "parking",
                    "place":           parking,
                    "arrive_at":       park_arrive,
                    "leave_at":        park_leave,
                    "enter_transport": None,
                    "exit_transport":  {"mode": "walk", "minutes": walk_min},
                    "travel_to_next_minutes": walk_min,
                })

        # ── 현재 장소 추가 ──
        result.append(item)

        # ── 다음 장소가 있으면 거리 체크 ──
        if idx < len(itinerary) - 1 and current_parking is not None:
            next_place = itinerary[idx + 1]["place"]
            next_lat   = next_place.get("lat", 0)
            next_lng   = next_place.get("lng", 0)

            dist = haversine(
                current_parking["lat"], current_parking["lng"],
                next_lat, next_lng
            )

            if dist > PARKING_REUSE_DISTANCE_KM:
                # 새 주차장 검색
                new_parking = await search_parking(next_lat, next_lng)
                if new_parking:
                    leave_at = item.get("leave_at", "09:00")

                    # 현재 장소 → 이전 주차장 복귀 (도보)
                    walk_back_min = travel_min(
                        haversine(lat, lng, current_parking["lat"], current_parking["lng"]),
                        WALK_SPEED_KMH
                    )
                    old_park_arrive = to_str(to_dt(leave_at) + timedelta(minutes=walk_back_min))

                    # 이전 주차장 → 새 주차장 (자동차)
                    car_min = travel_min(
                        haversine(current_parking["lat"], current_parking["lng"],
                                  new_parking["lat"], new_parking["lng"]),
                        CAR_SPEED_KMH
                    )
                    new_park_arrive = to_str(to_dt(old_park_arrive) + timedelta(minutes=car_min))
                    new_park_leave  = to_str(to_dt(new_park_arrive) + timedelta(minutes=1))

                    # 새 주차장 → 다음 장소 (도보)
                    walk_to_next = travel_min(
                        haversine(new_parking["lat"], new_parking["lng"], next_lat, next_lng),
                        WALK_SPEED_KMH
                    )

                    # 이전 주차장 복귀 블록 (arrive~leave = 전체 이동 구간)
                    result.append({
                        "type":            "parking",
                        "place":           current_parking,
                        "arrive_at":       old_park_arrive,
                        "leave_at":        new_park_leave,
                        "enter_transport": {"mode": "walk", "minutes": walk_back_min},
                        "exit_transport":  {"mode": "car",  "minutes": car_min},
                        "travel_to_next_minutes": car_min,
                    })

                    # 새 주차장 블록 (진입/출차 정보만)
                    result.append({
                        "type":            "parking",
                        "place":           new_parking,
                        "arrive_at":       None,
                        "leave_at":        None,
                        "enter_transport": {"mode": "car",  "minutes": car_min},
                        "exit_transport":  {"mode": "walk", "minutes": walk_to_next},
                        "travel_to_next_minutes": walk_to_next,
                    })

                    current_parking = new_parking

                    # travel_to_next_minutes 업데이트 (장소 → 이전 주차장 도보)
                    result[-3]["travel_to_next_minutes"] = walk_back_min

    return result


# ─── only 케이스 총 후보 수 ───
ONLY_TOTAL_CANDIDATES = {1: 3, 2: 6, 3: 10, 4: 15}


# ─── [노드] 일정 계획 리스트 작성 ───
async def plan_itinerary(state: dict) -> dict:
    valid_routes_by_day = state.get("valid_routes_by_day", {})
    all_routes_by_day   = state.get("all_routes_by_day", {})
    transport_kr        = state["user_input"].get("transport_kr", "도보")
    route_type          = state["user_input"].get("route_type", "only")
    travel_days         = state["user_input"].get("travel_days", 1)
    warnings: list[str] = []

    itineraries_by_day: dict[int, list[list[dict]]] = {}

    # ── 케이스 1 (only): 전체 동선 → day별 균등 배분 ─────────────────
    if route_type == "only":
        valid_routes = valid_routes_by_day.get(1, [])
        if not valid_routes:
            valid_routes = all_routes_by_day.get(1, [])
        if not valid_routes:
            warnings.append("only 케이스 동선 없음 → 실패")
            return {"itineraries_by_day": {}, "warnings": warnings, "step": "failed"}

        total_needed  = ONLY_TOTAL_CANDIDATES.get(travel_days, 3)
        sorted_routes = sorted(valid_routes, key=lambda x: x["total_score"], reverse=True)
        top_routes    = sorted_routes[:total_needed]

        # 주차장 추가
        final_itineraries = []
        for r in top_routes:
            if transport_kr == "자동차":
                itinerary = await add_parking_to_itinerary(r["itinerary"])
            else:
                itinerary = r["itinerary"]
            final_itineraries.append(itinerary)

        # day당 3개씩 배분
        for day_number in range(1, travel_days + 1):
            day_slice = final_itineraries[(day_number - 1) * 3 : day_number * 3]
            if not day_slice:
                warnings.append(f"[only] day{day_number} 동선 없음 → 실패")
                return {"itineraries_by_day": {}, "warnings": warnings, "step": "failed"}
            itineraries_by_day[day_number] = day_slice
            warnings.append(f"[only] day{day_number} 동선 후보: {len(day_slice)}개")

        return {
            "itineraries_by_day": itineraries_by_day,
            "warnings":           warnings,
            "step":               "itinerary_planned",
        }

        return {
            "itineraries_by_day": itineraries_by_day,
            "warnings":           warnings,
            "step":               "itinerary_planned",
        }

    # ── 케이스 2 (endpoint): day별 상위 5개 추출 ─────────────────────
    for day_number in sorted(valid_routes_by_day.keys()):
        valid_routes = valid_routes_by_day[day_number]

        if not valid_routes:
            warnings.append(f"day{day_number} 유효 동선 없음 → 전체 동선 사용")
            valid_routes = all_routes_by_day.get(day_number, [])

        if not valid_routes:
            warnings.append(f"day{day_number} 동선 없음 → 실패")
            return {
                "itineraries_by_day": {},
                "warnings":           warnings,
                "step":               "failed",
            }

        top_routes = sorted(valid_routes, key=lambda x: x["total_score"], reverse=True)[:MAX_ITINERARIES_PER_DAY]

        final_itineraries = []
        for r in top_routes:
            if transport_kr == "자동차":
                itinerary = await add_parking_to_itinerary(r["itinerary"])
            else:
                itinerary = r["itinerary"]
            final_itineraries.append(itinerary)

        itineraries_by_day[day_number] = final_itineraries
        warnings.append(f"day{day_number} 동선 후보: {len(final_itineraries)}개")

    return {
        "itineraries_by_day": itineraries_by_day,
        "warnings":           warnings,
        "step":               "itinerary_planned",
    }