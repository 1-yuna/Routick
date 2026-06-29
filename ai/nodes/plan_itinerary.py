# ─────────────────────────────────────────────────────────────────────
# plan_itinerary
# ─────────────────────────────────────────────────────────────────────
# 점수 기반 day별 상위 5개 추출 + 주차장 추가
#
# 흐름:
#   1. 주차장 거점 정보 추가 (transport=car인 경우만)
#      - 동선 내 장소 순회하며 current_parking 기준으로 주차장 추가/갱신
#      - 1km 이내: 기존 주차장 유지, 1km 초과: 새 주차장 검색
#      - enterTransport/exitTransport 포함한 parking 블록 구성
#   2. total_score 내림차순 정렬 후 day별 상위 5개 반환
#      유효 동선 1개 이상이면 진행, 없으면 실패 응답
# ─────────────────────────────────────────────────────────────────────

import math
import os
import httpx
from datetime import datetime, timedelta

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# ─── day별 최대 동선 수 ───
MAX_ITINERARIES_PER_DAY = 5

# ─── 주차장 재검색 기준 거리 (km) ───
PARKING_REUSE_DISTANCE_KM = 1.0

# ─── 이동 속도 ───
CAR_SPEED_KMH  = 30.0
WALK_SPEED_KMH = 4.0


# ─── Haversine ───
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def travel_min(dist_km: float, speed_kmh: float) -> int:
    return max(1, round((dist_km / speed_kmh) * 60))


def to_dt(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── 주차장 검색 ───
async def search_parking(lat: float, lng: float, radius_m: int = 500) -> dict | None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                "https://dapi.kakao.com/v2/local/search/category.json",
                headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"},
                params={
                    "category_group_code": "PK6",
                    "x": lng,
                    "y": lat,
                    "radius": radius_m,
                    "size": 1,
                },
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


# ─── 동선에 주차장 추가 + 전체 시간 재계산 ───
async def add_parking_to_itinerary(itinerary: list[dict]) -> list[dict]:
    if not itinerary:
        return itinerary

    from utils.route.greedy_nn import STAY_MINUTES

    # ── 1단계: 주차장 삽입 위치 결정 ──
    # (place_item, parking_before, parking_after) 구조로 계획 수립
    segments = []  # 각 장소 + 앞뒤 주차장 정보
    current_parking = None

    for idx, item in enumerate(itinerary):
        lat = item["place"].get("lat", 0)
        lng = item["place"].get("lng", 0)

        parking_before = None
        parking_after  = None

        if current_parking is None:
            # 첫 장소: 근처 주차장 검색
            parking = await search_parking(lat, lng)
            if parking:
                current_parking = parking
                parking_before = parking

        # 다음 장소가 있으면 거리 체크
        if idx < len(itinerary) - 1:
            next_lat = itinerary[idx + 1]["place"].get("lat", 0)
            next_lng = itinerary[idx + 1]["place"].get("lng", 0)
            dist_to_next = haversine(
                current_parking["lat"], current_parking["lng"],
                next_lat, next_lng
            ) if current_parking else 0

            if dist_to_next > PARKING_REUSE_DISTANCE_KM:
                new_parking = await search_parking(next_lat, next_lng)
                if new_parking:
                    parking_after = {"old": current_parking, "new": new_parking}
                    current_parking = new_parking

        segments.append({
            "item":           item,
            "parking_before": parking_before,
            "parking_after":  parking_after,
        })

    # ── 2단계: 시간 재계산하며 블록 구성 ──
    result       = []
    current_time = to_dt(itinerary[0].get("arrive_at", "09:00"))

    for seg_idx, seg in enumerate(segments):
        item           = seg["item"]
        parking_before = seg["parking_before"]
        parking_after  = seg["parking_after"]
        place          = item["place"]
        bucket         = place.get("bucket", "activity")
        stay           = STAY_MINUTES.get(bucket, 90)

        # 주차장 before (첫 장소 진입 전)
        if parking_before:
            walk_min = travel_min(
                haversine(parking_before["lat"], parking_before["lng"],
                          place.get("lat", 0), place.get("lng", 0)),
                WALK_SPEED_KMH
            )
            park_arrive = to_str(current_time - timedelta(minutes=walk_min + 1))
            park_leave  = to_str(current_time - timedelta(minutes=walk_min))
            result.append({
                "type":            "parking",
                "place":           {**parking_before, "bucket": "parking"},
                "arrive_at":       park_arrive,
                "leave_at":        park_leave,
                "enter_transport": None,
                "exit_transport":  {"mode": "walk", "minutes": walk_min},
            })

        # 장소
        arrive_dt = current_time
        leave_dt  = arrive_dt + timedelta(minutes=stay)
        result.append({
            **item,
            "arrive_at": to_str(arrive_dt),
            "leave_at":  to_str(leave_dt),
        })
        current_time = leave_dt

        # 주차장 after (이전 주차장 복귀 → 새 주차장)
        if parking_after:
            old_park = parking_after["old"]
            new_park = parking_after["new"]
            next_place = segments[seg_idx + 1]["item"]["place"] if seg_idx + 1 < len(segments) else None

            # 현재 장소 → 이전 주차장 복귀 (도보)
            walk_back_min = travel_min(
                haversine(place.get("lat", 0), place.get("lng", 0),
                          old_park["lat"], old_park["lng"]),
                WALK_SPEED_KMH
            )
            old_park_arrive = to_str(current_time + timedelta(minutes=walk_back_min))

            # 이전 주차장 → 새 주차장 (자동차)
            car_min = travel_min(
                haversine(old_park["lat"], old_park["lng"],
                          new_park["lat"], new_park["lng"]),
                CAR_SPEED_KMH
            )
            new_park_arrive = to_str(to_dt(old_park_arrive) + timedelta(minutes=car_min))
            new_park_leave  = to_str(to_dt(new_park_arrive) + timedelta(minutes=1))

            # 새 주차장 → 다음 장소 (도보)
            walk_to_next = travel_min(
                haversine(new_park["lat"], new_park["lng"],
                          next_place.get("lat", 0), next_place.get("lng", 0)),
                WALK_SPEED_KMH
            ) if next_place else 0

            # 이전 주차장 복귀 블록
            result.append({
                "type":            "parking",
                "place":           {**old_park, "bucket": "parking"},
                "arrive_at":       old_park_arrive,
                "leave_at":        None,
                "enter_transport": {"mode": "walk", "minutes": walk_back_min},
                "exit_transport":  {"mode": "car",  "minutes": car_min},
            })

            # 새 주차장 블록
            result.append({
                "type":            "parking",
                "place":           {**new_park, "bucket": "parking"},
                "arrive_at":       new_park_arrive,
                "leave_at":        new_park_leave,
                "enter_transport": {"mode": "car",  "minutes": car_min},
                "exit_transport":  {"mode": "walk", "minutes": walk_to_next},
            })

            # 다음 장소 시작 시간 갱신 (주차장 이동 포함)
            current_time = to_dt(new_park_leave) + timedelta(minutes=walk_to_next)

        elif seg_idx + 1 < len(segments):
            # 주차장 없는 케이스: 현재 주차장 → 다음 장소까지 도보 이동시간 반영
            next_place = segments[seg_idx + 1]["item"]["place"]
            current_parking_for_walk = seg["parking_before"] or (
                segments[seg_idx - 1]["parking_after"]["new"] if seg_idx > 0 and segments[seg_idx - 1]["parking_after"] else None
            )
            if current_parking_for_walk:
                walk_min = travel_min(
                    haversine(current_parking_for_walk["lat"], current_parking_for_walk["lng"],
                              next_place.get("lat", 0), next_place.get("lng", 0)),
                    WALK_SPEED_KMH
                )
            else:
                walk_min = travel_min(
                    haversine(place.get("lat", 0), place.get("lng", 0),
                              next_place.get("lat", 0), next_place.get("lng", 0)),
                    CAR_SPEED_KMH
                )
            current_time = leave_dt + timedelta(minutes=walk_min)

    # ── 3단계: travel_to_next_minutes 재계산 (주차장 이동시간 포함) ──
    # 결과 리스트에서 place 아이템과 그 다음 place 아이템 사이의 실제 경과 시간 계산
    place_indices = [i for i, r in enumerate(result) if r.get("place", {}).get("bucket") != "parking"]
    for idx, pi in enumerate(place_indices[:-1]):
        next_pi = place_indices[idx + 1]
        try:
            leave  = result[pi].get("leave_at", "")
            arrive = result[next_pi].get("arrive_at", "")
            if leave and arrive:
                diff = (to_dt(arrive) - to_dt(leave)).total_seconds() / 60
                result[pi]["travel_to_next_minutes"] = max(0, int(diff))
        except Exception:
            pass
    if place_indices:
        result[place_indices[-1]]["travel_to_next_minutes"] = 0

    return result


# ─── [노드] 일정 계획 리스트 작성 ───
async def plan_itinerary(state: dict) -> dict:
    valid_routes_by_day = state.get("valid_routes_by_day", {})
    all_routes_by_day   = state.get("all_routes_by_day", {})
    transport_kr        = state["user_input"].get("transport_kr", "도보")
    warnings: list[str] = []

    itineraries_by_day: dict[int, list[list[dict]]] = {}

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

        # total_score 내림차순 정렬 후 상위 5개
        top_routes = sorted(valid_routes, key=lambda x: x["total_score"], reverse=True)[:MAX_ITINERARIES_PER_DAY]

        # 주차장 추가 (car인 경우만)
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