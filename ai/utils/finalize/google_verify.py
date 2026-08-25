# ─────────────────────────────────────────────────────────────────────
# google_verify
# ─────────────────────────────────────────────────────────────────────
# 구글 Places API로 실제 방문 가능한지(영업시간) 검증 + 휴무 시 대체 장소 탐색
#   - 구글에 정보가 없으면 "정보없음" (휴무로 간주하지 않음 — 대체 탐색 트리거 아님)
#   - 영업시간과 겹치지 않으면(휴무) "영업 종료" → 대체 탐색
#   - 대체 후보: 같은 bucket(활동↔활동/카페↔카페/밥↔밥) + 가까운 순 +
#     앞뒤 장소와 이동 가능(travel_between 통과) + 그 후보도 영업 중이어야 채택
# ─────────────────────────────────────────────────────────────────────

import os
import re
from datetime import datetime

import httpx

from utils.route.route_timing import haversine_km, travel_between

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GOOGLE_FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
GOOGLE_DETAILS_URL    = "https://maps.googleapis.com/maps/api/place/details/json"

# 요일 인덱스(0=월) → 구글 opening_hours periods의 day(0=일) 변환
WEEKDAY_TO_GOOGLE_DAY = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}


def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# ─── 장소명 → 구글 place_id 조회 ───
async def _find_place_id(client: httpx.AsyncClient, name: str, lat: float, lng: float) -> str | None:
    try:
        resp = await client.get(
            GOOGLE_FIND_PLACE_URL,
            params={
                "input": name, "inputtype": "textquery",
                "locationbias": f"point:{lat},{lng}", "fields": "place_id",
                "key": GOOGLE_API_KEY,
            },
        )
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        return candidates[0]["place_id"] if candidates else None
    except Exception:
        return None


# ─── 구글 place_id → 상세정보(사진, 영업시간) 조회 ───
async def _fetch_place_details(client: httpx.AsyncClient, google_place_id: str) -> dict:
    try:
        resp = await client.get(
            GOOGLE_DETAILS_URL,
            params={"place_id": google_place_id, "fields": "photos,opening_hours", "key": GOOGLE_API_KEY},
        )
        resp.raise_for_status()
        result = resp.json().get("result", {})

        photo_url = None
        photos = result.get("photos") or []
        if photos and photos[0].get("photo_reference"):
            photo_url = (
                "https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=800&photo_reference={photos[0]['photo_reference']}&key={GOOGLE_API_KEY}"
            )
        return {"src": photo_url, "opening_hours": result.get("opening_hours")}
    except Exception:
        return {}


# ─── 장소 1개 구글 정보 보강 — 정보 없으면 "정보없음", 영업 여부는 방문시각 확정 후 별도 판정 ───
async def enrich_with_google(client: httpx.AsyncClient, place: dict) -> dict:
    google_place_id = await _find_place_id(client, place.get("name", ""), place.get("lat", 0), place.get("lng", 0))
    if not google_place_id:
        return {**place, "src": None, "status": "정보없음", "_opening_hours": None}

    details = await _fetch_place_details(client, google_place_id)
    return {
        **place,
        "src":            details.get("src"),
        "status":         "정보없음" if details.get("opening_hours") is None else "영업 정보 확인중",
        "_opening_hours": details.get("opening_hours"),
    }


def _parse_weekday_text(text: str, arrive_at: str, leave_at: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    if "open 24 hours" in lower:
        return True
    if "closed" in lower:
        return False
    match = re.search(r":\s*(.+)", text)
    if not match:
        return False
    parts = re.split(r"[–\-]", match.group(1).strip())
    if len(parts) != 2:
        return False
    try:
        open_t  = datetime.strptime(parts[0].strip(), "%I:%M %p")
        close_t = datetime.strptime(parts[1].strip(), "%I:%M %p")
        open_min, close_min = open_t.hour * 60 + open_t.minute, close_t.hour * 60 + close_t.minute
        arrive_min, leave_min = _to_minutes(arrive_at), _to_minutes(leave_at)
        if close_min == 0:
            close_min = 24 * 60
        if close_min < open_min:
            close_min += 24 * 60
        return open_min <= arrive_min and leave_min <= close_min
    except Exception:
        return False


# ─── 방문 시간(도착~출발)이 영업시간 안에 드는지 — 정보 없으면 보수적으로 통과 처리 ───
def is_open(opening_hours: dict | None, weekday_idx: int, arrive_at: str, leave_at: str) -> bool:
    if not opening_hours:
        return True
    periods = opening_hours.get("periods")
    if not periods:
        return True

    if (len(periods) == 1
            and periods[0].get("open", {}).get("day") == 0
            and periods[0].get("open", {}).get("time") == "0000"
            and not periods[0].get("close")):
        return True  # 24시간 영업

    google_day = WEEKDAY_TO_GOOGLE_DAY.get(weekday_idx, 0)
    arrive_min, leave_min = _to_minutes(arrive_at), _to_minutes(leave_at)

    for period in periods:
        open_info, close_info = period.get("open", {}), period.get("close")
        if open_info.get("day") != google_day:
            continue
        open_min = int(open_info.get("time", "0000")[:2]) * 60 + int(open_info.get("time", "0000")[2:])
        if close_info:
            close_min = int(close_info.get("time", "2359")[:2]) * 60 + int(close_info.get("time", "2359")[2:])
            if close_info.get("day") != open_info.get("day"):
                close_min += 24 * 60
        else:
            close_min = 24 * 60
        if open_min <= arrive_min and leave_min <= close_min:
            return True

    weekday_text_list = opening_hours.get("weekday_text", [])
    if len(weekday_text_list) == 7:
        return _parse_weekday_text(weekday_text_list[weekday_idx], arrive_at, leave_at)
    return False


# ─── 휴무로 확인된 장소를 대체할 후보 탐색 (같은 bucket + 가까운 순) ───
async def find_replacement(
    client: httpx.AsyncClient,
    target: dict,
    arrive_at: str,
    leave_at: str,
    pool: list[dict],
    excluded_ids: set[str],
    weekday_idx: int,
    prev_coord: tuple | None,
    next_coord: tuple | None,
    transport: str,
) -> dict | None:
    candidates = [
        p for p in pool
        if p.get("bucket") == target.get("bucket")
        and p["id"] not in excluded_ids
        and p["id"] != target["id"]
    ]
    candidates.sort(key=lambda c: haversine_km(target["lat"], target["lng"], c["lat"], c["lng"]))

    for c in candidates:
        if prev_coord:
            t1 = travel_between(prev_coord[0], prev_coord[1], c["lat"], c["lng"], transport)
            if not t1["feasible"]:
                continue
        if next_coord:
            t2 = travel_between(c["lat"], c["lng"], next_coord[0], next_coord[1], transport)
            if not t2["feasible"]:
                continue

        c_enriched = await enrich_with_google(client, c)
        if not is_open(c_enriched.get("_opening_hours"), weekday_idx, arrive_at, leave_at):
            continue

        return {**c_enriched, "status": "영업 중"}

    return None