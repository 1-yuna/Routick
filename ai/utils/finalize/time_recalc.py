# ─────────────────────────────────────────────────────────────────────
# time_recalc
# ─────────────────────────────────────────────────────────────────────
# 시간 재계산 (+ 자동차인 경우 주차장 정보 추가)
#
# route_build 단계까지는 슬롯 간 "이동시간(분)"만 갖고 있고 실제 시계 시간
# (도착/출발 시각)은 계산돼 있지 않음 — 이 노드가 그걸 처음 계산함.
#
# 내부적으로 place/parking/start/end를 하나의 순서열("stops")로 통일해서 다룸:
#   {"kind": "start"|"place"|"parking"|"end", "place": {...}}
# 자동차 + 주차장이 섞이면 구간마다 이동수단이 달라지므로(주차장↔장소는 도보,
# 주차장↔주차장은 자동차) kind 조합으로 구간별 이동수단을 그때그때 판단함
# ─────────────────────────────────────────────────────────────────────

import os
from datetime import datetime, timedelta

import httpx

from utils.route.route_timing import travel_between, haversine_km, stay_minutes

KAKAO_API_KEY        = os.getenv("KAKAO_REST_API_KEY")
KAKAO_CATEGORY_URL   = "https://dapi.kakao.com/v2/local/search/category.json"
PARKING_CATEGORY_CODE = "PK6"
PARKING_REUSE_DISTANCE_KM = 1.0


def to_dt(hhmm: str) -> datetime:
    return datetime.strptime(hhmm, "%H:%M")


def to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ─── route_build 결과(places/legs/start_block/end_block)를 stops 순서열로 변환 ───
def route_to_stops(route: dict) -> list[dict]:
    stops = []
    if route.get("start_block"):
        stops.append({"kind": "start", "place": {"lat": route["start_block"]["lat"], "lng": route["start_block"]["lng"]}})
    for p in route["places"]:
        stops.append({"kind": "place", "place": p})
    if route.get("end_block"):
        stops.append({"kind": "end", "place": {"lat": route["end_block"]["lat"], "lng": route["end_block"]["lng"]}})
    return stops


# ─── 구간 이동수단 판단 ───
# - 출발지(start)에서 나가는 구간: 차를 가진 채로 시작하는 구간이므로 그날 실제 transport
#   그대로 (자동차면 첫 주차장까지 "운전", 자동차가 아니면 기존 도보/택시 로직 그대로)
# - 주차장 ↔ 주차장: 차를 재배치하는 구간 → 자동차
# - 주차장 ↔ 장소: 차는 세워두고 사람만 오가는 구간 → 도보
# - 장소 ↔ 장소인데 자동차인 날: 같은 주차장을 재사용 중(주차장 재배치가 없었던 구간)이라는
#   뜻이므로 차는 그대로 세워져 있고 사람은 도보로 이동 → 도보
#   (자동차가 아닌 날은 원래 그날 transport 그대로 — 기존 도보/택시 전환 로직 유지)
def _leg_transport(from_kind: str, to_kind: str, day_transport: str) -> str:
    if from_kind == "start":
        return day_transport
    if from_kind == "parking" and to_kind == "parking":
        return "car"
    if from_kind == "parking" or to_kind == "parking":
        return "walk"
    if day_transport == "car":
        return "walk"
    return day_transport


# ─── stops 전체를 처음부터 다시 훑으며 도착/출발 시각 + 구간 이동시간 계산 ───
# 장소 교체·주차장 삽입 등으로 순서가 바뀔 때마다 이 함수를 다시 돌리면 항상 정합성 보장
# (6~14개 정도의 짧은 리스트라 매번 처음부터 다시 계산해도 비용 부담 없음)
def recompute_timeline(stops: list[dict], start_time: str, transport: str) -> list[dict]:
    stops = [dict(s) for s in stops]
    current = to_dt(start_time)

    for i, s in enumerate(stops):
        kind = s["kind"]
        if kind == "start":
            s["leave_at"] = to_str(current)
        elif kind == "end":
            s["arrive_at"] = to_str(current)
        else:  # place / parking
            s["arrive_at"] = to_str(current)
            stay = 0 if kind == "parking" else stay_minutes(s["place"])
            current = current + timedelta(minutes=stay)
            s["leave_at"] = to_str(current)

        if i < len(stops) - 1:
            nxt = stops[i + 1]
            leg_transport = _leg_transport(kind, nxt["kind"], transport)
            t = travel_between(s["place"]["lat"], s["place"]["lng"], nxt["place"]["lat"], nxt["place"]["lng"], leg_transport)
            s["travel_to_next_minutes"] = t["minutes"]
            s["travel_mode"] = t["mode"]
            current = current + timedelta(minutes=t["minutes"])

    return stops


# ─── 주차장 검색 (카카오 카테고리 검색, 반경 500m 내 1곳) ───
async def search_parking(client: httpx.AsyncClient, lat: float, lng: float, radius_m: int = 500) -> dict | None:
    try:
        resp = await client.get(
            KAKAO_CATEGORY_URL,
            headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"},
            params={"category_group_code": PARKING_CATEGORY_CODE, "x": lng, "y": lat, "radius": radius_m, "size": 1},
        )
        resp.raise_for_status()
        docs = resp.json().get("documents", [])
        if not docs:
            return None
        doc = docs[0]
        return {
            "id":       doc["id"],
            "name":     doc["place_name"],
            "address":  doc.get("road_address_name") or doc.get("address_name", ""),
            "lat":      float(doc["y"]),
            "lng":      float(doc["x"]),
            "bucket":   "parking",
        }
    except Exception:
        return None


# ─── stops(주차장 없는 상태)에 주차장 블록 삽입 (자동차 전용) ───
# 매 place/end 지점마다 "지금 확보해둔 주차장"이 1km 이내면 그대로 재사용,
# 아니면 이전 주차장 복귀 블록 + 새 주차장 블록을 끼워 넣고 갱신
async def add_parking_stops(stops: list[dict], client: httpx.AsyncClient) -> list[dict]:
    result: list[dict] = []
    current_parking: dict | None = None

    for s in stops:
        if s["kind"] == "start":
            result.append(s)
            continue

        coord = s["place"]
        if current_parking is None:
            p = await search_parking(client, coord["lat"], coord["lng"])
            if p:
                result.append({"kind": "parking", "place": p})
                current_parking = p
        else:
            dist = haversine_km(current_parking["lat"], current_parking["lng"], coord["lat"], coord["lng"])
            if dist > PARKING_REUSE_DISTANCE_KM:
                new_p = await search_parking(client, coord["lat"], coord["lng"])
                if new_p:
                    result.append({"kind": "parking", "place": current_parking})
                    result.append({"kind": "parking", "place": new_p})
                    current_parking = new_p

        result.append(s)

    return result