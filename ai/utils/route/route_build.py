# ─────────────────────────────────────────────────────────────────────
# route_build
# ─────────────────────────────────────────────────────────────────────
# 동선 하나 생성 (그리디)
#
# 슬롯 패턴: 카페/활동 → 밥 → 카페/활동 → 카페/활동 → 밥 → 카페/활동
# 슬롯 선택 규칙: 이동시간 제한 내 후보 중 적합도 점수 최고
#   - 마지막 슬롯 + endpoint(도착지 좌표 있음): 도착지에 가까운 절반 후보 중 점수 최고
#     (하루 대부분은 mid 반경으로 뽑힌 shortlist 안에서 자유롭게 놀고,
#      마지막 활동만 도착지 방향으로 붙이는 식)
#   - 앵커(query_name 있는 장소)가 아직 없고 후보 중 하나라도 있으면 그 앵커를 우선 채택
#     (best-effort 포함 — 이동 가능 후보에 앵커가 아예 없으면 포기)
# ─────────────────────────────────────────────────────────────────────

from utils.route.route_constraints import (
    violates_brand_cap, violates_category_cap, violates_consecutive_cafe,
    register_place, is_anchor,
)
from utils.route.route_timing import travel_between, haversine_km

SLOT_PATTERN_6 = ["flex", "food", "flex", "flex", "food", "flex"]

# 5슬롯 폴백 패턴 — "최적 일정 선택" 노드가 검증 실패 시 완화된 조건으로 재생성할 때 사용
SLOT_PATTERN_5 = ["flex", "food", "flex", "food", "flex"]


# ─── 슬롯 하나의 후보 풀 (bucket/brand/category/연속카페 제약만 적용, 이동시간은 아직) ───
def _slot_candidates(
    pool: list[dict],
    used_ids: set,
    used_brands: set,
    used_categories: set,
    last_bucket: str | None,
) -> list[dict]:
    out = []
    for p in pool:
        if p["id"] in used_ids:
            continue
        if violates_brand_cap(p, used_brands):
            continue
        if violates_category_cap(p, used_categories):
            continue
        if violates_consecutive_cafe(p, last_bucket):
            continue
        out.append(p)
    return out


# ─── 이동시간 제한을 통과하는 후보만, travel 정보를 붙여서 반환 ───
def _feasible_with_travel(candidates: list[dict], from_lat: float, from_lng: float, transport: str) -> list[tuple]:
    out = []
    for p in candidates:
        travel = travel_between(from_lat, from_lng, p["lat"], p["lng"], transport)
        if travel["feasible"]:
            out.append((p, travel))
    return out


# ─── 마지막 슬롯: 도착지에 가까운 절반만 남기기 (도착지 방향 편향) ───
def _bias_toward_end(feasible: list[tuple], end_lat: float, end_lng: float) -> list[tuple]:
    if not feasible:
        return feasible
    ranked = sorted(feasible, key=lambda pt: haversine_km(pt[0]["lat"], pt[0]["lng"], end_lat, end_lng))
    half = max(1, len(ranked) // 2)
    return ranked[:half]


# ─── 후보 중 하나 선택 (앵커 우선 → 없으면 점수 최고) ───
def _pick(feasible: list[tuple], route_has_anchor: bool) -> tuple:
    if not route_has_anchor:
        anchors = [pt for pt in feasible if is_anchor(pt[0])]
        if anchors:
            return max(anchors, key=lambda pt: pt[0]["total_score"])
    return max(feasible, key=lambda pt: pt[0]["total_score"])


# ─── 동선 하나 생성 (시작 장소 1개로부터 그리디하게 slot_pattern 길이만큼 채움) ───
# start_coord / end_coord: endpoint 케이스의 실제 출발지·도착지 좌표 (only면 둘 다 None)
# slot_pattern: 기본 6슬롯(SLOT_PATTERN_6). "최적 일정 선택" 노드의 완화 재생성 시 SLOT_PATTERN_5로 교체
def build_route(
    start_place: dict,
    flex_pool: list[dict],
    food_pool: list[dict],
    transport: str,
    route_type: str,
    start_coord: tuple | None,
    end_coord: tuple | None,
    slot_pattern: list[str] = SLOT_PATTERN_6,
) -> dict | None:
    used_ids:        set = {start_place["id"]}
    used_brands:      set = set()
    used_categories:   set = set()
    register_place(start_place, used_brands, used_categories)

    places = [start_place]
    legs   = []  # 슬롯 간 이동 정보 (len = len(slot_pattern) - 1)
    route_has_anchor = is_anchor(start_place)
    current_lat, current_lng = start_place["lat"], start_place["lng"]
    last_bucket = start_place.get("bucket")

    for slot_index in range(1, len(slot_pattern)):
        slot_type = slot_pattern[slot_index]
        pool = food_pool if slot_type == "food" else flex_pool

        candidates = _slot_candidates(pool, used_ids, used_brands, used_categories, last_bucket)
        feasible = _feasible_with_travel(candidates, current_lat, current_lng, transport)
        if not feasible:
            return None

        is_last_slot = slot_index == len(slot_pattern) - 1
        if is_last_slot and route_type == "endpoint" and end_coord is not None:
            biased = _bias_toward_end(feasible, end_coord[0], end_coord[1])
            chosen_place, chosen_travel = _pick(biased, route_has_anchor)
        else:
            chosen_place, chosen_travel = _pick(feasible, route_has_anchor)

        if is_anchor(chosen_place):
            route_has_anchor = True

        legs.append(chosen_travel)
        places.append(chosen_place)
        used_ids.add(chosen_place["id"])
        register_place(chosen_place, used_brands, used_categories)
        current_lat, current_lng = chosen_place["lat"], chosen_place["lng"]
        last_bucket = chosen_place.get("bucket")

    start_block = None
    end_block = None
    if route_type == "endpoint" and start_coord is not None:
        start_block = {
            "lat": start_coord[0], "lng": start_coord[1],
            "travel_to_first": travel_between(start_coord[0], start_coord[1], places[0]["lat"], places[0]["lng"], transport),
        }
    if route_type == "endpoint" and end_coord is not None:
        end_block = {
            "lat": end_coord[0], "lng": end_coord[1],
            "travel_from_last": travel_between(places[-1]["lat"], places[-1]["lng"], end_coord[0], end_coord[1], transport),
        }

    return {
        "places":      [{**p, "slot": i, "slot_type": slot_pattern[i]} for i, p in enumerate(places)],
        "legs":        legs,
        "start_block": start_block,
        "end_block":   end_block,
        "has_anchor":  route_has_anchor,
        "total_score": round(sum(p["total_score"] for p in places), 1),
    }