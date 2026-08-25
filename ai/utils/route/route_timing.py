# ─────────────────────────────────────────────────────────────────────
# route_timing
# ─────────────────────────────────────────────────────────────────────
# 좌표 간 거리/이동시간 계산 + 체류시간(활동 시간대) 분류
#
# 이동시간 규칙:
#   - 차량 없음: 도보(4km/h) 기준 20분 이하면 도보 / 초과 시 택시(자동차 속도 기준)로 전환,
#     택시는 최대 15분까지만 허용
#   - 차량 있음: 자동차(30km/h) 기준 최대 30분까지 허용
#
# 체류시간 규칙 (기본):
#   - 밥 90분 / 카페 60분
#   - 활동: 해수욕장·더베이101·방탈출 등 큰 활동 120분,
#           포토이즘·오락실 등 작은 단위 활동 30분,
#           그 외 활동은 90분(기본값)
# ─────────────────────────────────────────────────────────────────────

import math

WALK_SPEED_KMH = 4.0
CAR_SPEED_KMH  = 30.0

WALK_SOFT_LIMIT_MIN = 20   # 차량 없음: 도보로 이 시간 넘으면 택시 전환
TAXI_HARD_LIMIT_MIN = 15   # 차량 없음: 택시 이동시간 상한
CAR_HARD_LIMIT_MIN  = 30   # 차량 있음: 자동차 이동시간 상한

STAY_MINUTES = {"food": 90, "cafe": 60, "activity": 90}

# 큰 단위 활동 (2시간) — 키워드 초안, 실제 서비스 반영 전 검수 필요
BIG_ACTIVITY_KEYWORDS = [
    "해수욕장", "해변", "더베이", "방탈출", "워터파크", "아쿠아리움", "테마파크", "놀이공원",
    "스키장", "서핑", "짚라인", "패러글라이딩", "등산", "트레킹", "박물관", "미술관",
    "전시관", "동물원", "식물원", "케이블카", "루지", "스케이트장", "온천", "스파",
]
BIG_ACTIVITY_STAY_MIN = 120

# 작은 단위 활동 (30분) — 키워드 초안, 실제 서비스 반영 전 검수 필요
SMALL_ACTIVITY_KEYWORDS = [
    "포토이즘", "인생네컷", "포토그레이", "포토부스", "셀프사진관", "네컷사진",
    "오락실", "인형뽑기", "VR방",
]
SMALL_ACTIVITY_STAY_MIN = 30


# ─── 두 좌표 간 직선거리 (km, 하버사인) ───
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─── 두 좌표 간 이동시간/수단 계산 ───
def travel_between(lat1: float, lng1: float, lat2: float, lng2: float, transport: str) -> dict:
    distance_km = haversine_km(lat1, lng1, lat2, lng2)

    if transport == "car":
        minutes = (distance_km / CAR_SPEED_KMH) * 60
        return {"mode": "car", "minutes": round(minutes, 1), "feasible": minutes <= CAR_HARD_LIMIT_MIN}

    walk_minutes = (distance_km / WALK_SPEED_KMH) * 60
    if walk_minutes <= WALK_SOFT_LIMIT_MIN:
        return {"mode": "walk", "minutes": round(walk_minutes, 1), "feasible": True}

    taxi_minutes = (distance_km / CAR_SPEED_KMH) * 60
    return {"mode": "taxi", "minutes": round(taxi_minutes, 1), "feasible": taxi_minutes <= TAXI_HARD_LIMIT_MIN}


# ─── 활동 체류시간(분) 분류 — 이름/카테고리 키워드 기반 ───
def _activity_stay_minutes(place: dict) -> int:
    name     = place.get("name", "") or ""
    category = place.get("category", "") or ""
    text = name + category

    if any(kw in text for kw in BIG_ACTIVITY_KEYWORDS):
        return BIG_ACTIVITY_STAY_MIN
    if any(kw in text for kw in SMALL_ACTIVITY_KEYWORDS):
        return SMALL_ACTIVITY_STAY_MIN
    return STAY_MINUTES["activity"]


# ─── 장소 하나의 체류시간(분) ───
def stay_minutes(place: dict) -> int:
    bucket = place.get("bucket", "activity")
    if bucket == "activity":
        return _activity_stay_minutes(place)
    return STAY_MINUTES.get(bucket, STAY_MINUTES["activity"])