# ─────────────────────────────────────────────────────────────────────
# collect_candidate_pool
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API로 raw 후보군 수집 + PostgreSQL 영구 저장
#
# 흐름 *(v3.1 — 앵커 중심 수집으로 개편)*:
#   1. 힌트 앵커 확정
#      - region_hint의 hint_keywords를 카카오 name 검색으로 실제 장소에 해소(resolve)
#      - 검색 안 잡히는 키워드(할루시네이션)는 버림
#      - 검색 radius를 기본 반경으로 제한 → 기본 반경 밖 앵커는 자동으로 걸러짐
#      → day별 hint_anchors: [{name, place_id, lat, lng}] 상태 저장
#   2. 앵커 주변 수집 (메인)
#      - 각 앵커 좌표 중심 앵커 소반경(도보 800m / 자동차 2km)에서
#        final_keywords 검색 (최대 2페이지)
#      - 결과에 nearest_hint / hint_dist_m 태깅, 앵커 자체는 is_hint_anchor=True
#   3. 보충 수집 (병행 폴백)
#      - 앵커 0개 → center 기본 반경 검색으로 전면 폴백 (기존 v2 방식)
#      - 앵커 1~2개 또는 앵커 수집 결과 30개 미만 → center 검색 병행
#        (점심·저녁 food 후보 최소량 확보 — 코스 생성 실패 방지)
#   4. 좌표 → 행정구역명 변환 (기존과 동일)
#   5. 병합 + dedup(place_id) → PostgreSQL upsert
# ─────────────────────────────────────────────────────────────────────

import asyncio
import httpx
import os

from utils.pool.kakao_search import (
    search_kakao_by_radius,
    kakao_keyword_search_radius,
    parse_kakao_doc,
    coord_to_region,
)
from utils.pool.db import upsert_places
from nodes.preprocess_input import haversine_km

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# 앵커 소반경 (travelDays 무관, travel_mode에만 의존)
ANCHOR_RADIUS_KM = {
    "walk": 0.8,
    "car":  2.0,
}
ANCHOR_SEARCH_PAGES = 2   # 앵커 주변 수집 페이지 수 (호출 폭증 방지)

MIN_ANCHORS   = 3    # 앵커가 이보다 적으면 보충 수집 병행
MIN_POOL_SIZE = 30   # 앵커 수집 결과가 이보다 적으면 보충 수집 병행


# ─── 1. 힌트 앵커 확정 (name 검색으로 해소) ───
async def _resolve_anchors(
    client:        httpx.AsyncClient,
    hint_keywords: list[str],
    center_lat:    float,
    center_lng:    float,
    radius_km:     float,
    day_number:    int,
    warnings:      list[str],
) -> list[dict]:
    """hint_keywords를 실제 장소로 해소.
    radius를 기본 반경으로 제한하므로 반경 밖 앵커는 카카오가 알아서 걸러줌."""
    radius_m = min(int(radius_km * 1000), 20000)
    anchors: list[dict] = []

    for kw in hint_keywords:
        try:
            docs = await kakao_keyword_search_radius(
                client, kw, center_lat, center_lng, radius_m, page=1,
            )
        except Exception as e:
            warnings.append(f"day{day_number} 앵커 검색 실패 [{kw}]: {type(e).__name__}")
            continue

        if not docs:
            warnings.append(f"day{day_number} 앵커 해소 실패 [{kw}] (미존재 또는 기본 반경 밖)")
            continue

        place = parse_kakao_doc(docs[0])
        place["is_hint_anchor"] = True
        place["nearest_hint"]   = kw
        place["hint_dist_m"]    = 0

        anchors.append({
            "name":          kw,                # LLM이 준 힌트 키워드
            "resolved_name": place["name"],     # 카카오에서 해소된 실제 장소명
            "place_id":      place["id"],
            "lat":           place["lat"],
            "lng":           place["lng"],
            "place":         place,
        })

    if anchors:
        warnings.append(
            f"day{day_number} 앵커 {len(anchors)}개 확정: "
            f"{[a['resolved_name'] for a in anchors]}"
        )
    return anchors


# ─── 2. 앵커 주변 수집 (메인) ───
async def _collect_around_anchors(
    anchors:  list[dict],
    keywords: list[str],
    transport: str,
    warnings: list[str],
) -> list[dict]:
    sub_radius_km = ANCHOR_RADIUS_KM.get(transport, ANCHOR_RADIUS_KM["walk"])
    merged: dict[str, dict] = {}

    # 앵커별 순차 처리 (동시 호출 폭주로 인한 rate limit 방지)
    for anchor in anchors:
        places, warns = await search_kakao_by_radius(
            keywords=keywords,
            lat=anchor["lat"], lng=anchor["lng"],
            radius_km=sub_radius_km,
            pages=ANCHOR_SEARCH_PAGES,
        )
        warnings.extend(warns)

        for p in places:
            dist_m = int(haversine_km(p["lat"], p["lng"], anchor["lat"], anchor["lng"]) * 1000)
            if p["id"] in merged:
                # 이미 다른 앵커에서 수집됨 → 더 가까운 앵커 기준으로 갱신
                if dist_m < merged[p["id"]].get("hint_dist_m", 10**9):
                    merged[p["id"]]["nearest_hint"] = anchor["name"]
                    merged[p["id"]]["hint_dist_m"]  = dist_m
            else:
                p["nearest_hint"] = anchor["name"]
                p["hint_dist_m"]  = dist_m
                merged[p["id"]] = p

    return list(merged.values())


# ─── day 1개 수집: 앵커 확정 → 앵커 주변(메인) → 조건부 보충(폴백) ───
async def _collect_day(
    client:     httpx.AsyncClient,
    day_info:   dict,
    keywords:   list[str],
    transport:  str,
    warnings:   list[str],
) -> tuple[list[dict], list[dict]]:
    """returns (unique_places, hint_anchors_meta)"""
    day_number = day_info["day_number"]
    lat        = day_info["center_lat"]
    lng        = day_info["center_lng"]
    radius_km  = day_info.get("radius_km", 2.0)

    # 1. 앵커 확정
    anchors = await _resolve_anchors(
        client, day_info.get("hint_keywords") or [],
        lat, lng, radius_km, day_number, warnings,
    )

    seen: set[str] = set()
    unique_places: list[dict] = []

    def _add(places: list[dict]):
        for p in places:
            if p["id"] not in seen:
                seen.add(p["id"])
                unique_places.append(p)

    # 앵커 자체도 후보로 포함 (is_hint_anchor=True)
    _add([a["place"] for a in anchors])

    # 2. 앵커 주변 수집 (메인)
    if anchors:
        cluster_places = await _collect_around_anchors(anchors, keywords, transport, warnings)
        _add(cluster_places)

    # 3. 보충 수집 (병행 폴백)
    need_supplement = (
        not anchors                          # a. 앵커 0개 → 전면 폴백 (기존 v2 방식)
        or len(anchors) < MIN_ANCHORS        # b. 앵커 1~2개 → 보충 병행
        or len(unique_places) < MIN_POOL_SIZE  # b. 수집 결과 부족 → 보충 병행
    )
    if need_supplement:
        reason = (
            "앵커 0개 → 전면 폴백" if not anchors
            else f"앵커 {len(anchors)}개/후보 {len(unique_places)}개 → 보충 병행"
        )
        warnings.append(f"day{day_number} center 기본 반경 수집 ({reason})")

        base_places, base_warnings = await search_kakao_by_radius(
            keywords=keywords, lat=lat, lng=lng, radius_km=radius_km,
        )
        warnings.extend(base_warnings)
        _add(base_places)

    if not unique_places:
        warnings.append(f"day{day_number} 후보 0개")

    # 상태 저장용 앵커 메타 (place dict 제외)
    anchors_meta = [
        {k: a[k] for k in ("name", "resolved_name", "place_id", "lat", "lng")}
        for a in anchors
    ]
    return unique_places, anchors_meta


# ─── [노드] Kakao API + DB ───
async def collect_candidate_pool(state: dict) -> dict:
    ui       = state["user_input"]
    warnings: list[str] = []
    errors:   list[str] = []

    keywords   = ui.get("final_keywords") or []
    days_info  = ui.get("days_info") or []
    route_type = ui.get("route_type", "only")
    transport  = ui.get("transport", "walk")

    if not keywords:
        warnings.append("final_keywords 비어있음 → 기본 키워드 사용")
        keywords = ["맛집", "카페"]

    if not days_info:
        errors.append("days_info 없음 — preprocess_input 점검 필요")
        return {
            "candidates":        [],
            "candidates_by_day": {},
            "user_input":        ui,
            "errors":            errors,
            "warnings":          warnings,
            "step":              "fetch_failed",
        }

    all_places:        list[dict]       = []
    candidates_by_day: dict[int, list]  = {}
    updated_days_info: list[dict]       = []

    days_raw = ui.get("days") or []

    async with httpx.AsyncClient(timeout=10.0) as client:

        # ── only 케이스: 목적지 좌표 동일하므로 수집 1회만 수행 ──────
        if route_type == "only":
            first_day_info = days_info[0]
            lat = first_day_info.get("center_lat")
            lng = first_day_info.get("center_lng")

            if lat is None or lng is None:
                warnings.append("only 케이스 좌표 없음")
            else:
                unique_places, anchors_meta = await _collect_day(
                    client, first_day_info, keywords, transport, warnings,
                )

                region = await coord_to_region(client, lat, lng)

                # candidates_by_day[1]에만 저장 (K-means 분할은 first_filter에서 처리)
                candidates_by_day[1] = unique_places
                all_places.extend(unique_places)
                updated_days_info.append({
                    **first_day_info,
                    "region":       region,
                    "hint_anchors": anchors_meta,
                })

        # ── endpoint 케이스: day별 독립 수집 (mid 좌표 기준) ──────────
        else:
            for day_info in days_info:
                day_number = day_info["day_number"]

                lat = day_info.get("center_lat")
                lng = day_info.get("center_lng")

                if lat is None or lng is None:
                    warnings.append(f"day{day_number} 좌표 없음 → 스킵")
                    continue

                unique_places, anchors_meta = await _collect_day(
                    client, day_info, keywords, transport, warnings,
                )

                day_raw = next((d for d in days_raw if d["day_number"] == day_number), None)
                if day_raw:
                    start_region, end_region = await asyncio.gather(
                        coord_to_region(client, day_raw["start_lat"], day_raw["start_lng"]),
                        coord_to_region(client, day_raw["end_lat"],   day_raw["end_lng"]),
                    )
                    day_info = {
                        **day_info,
                        "start_region":    start_region,
                        "end_region":      end_region,
                        "start_lat":       day_raw.get("start_lat"),
                        "start_lng":       day_raw.get("start_lng"),
                        "start_name":      day_raw.get("start_name"),
                        "start_address":   day_raw.get("start_address"),
                        "start_place_id":  day_raw.get("start_place_id"),
                        "end_lat":         day_raw.get("end_lat"),
                        "end_lng":         day_raw.get("end_lng"),
                        "end_name":        day_raw.get("end_name"),
                        "end_address":     day_raw.get("end_address"),
                        "end_place_id":    day_raw.get("end_place_id"),
                        "mid_name":        day_raw.get("mid_name"),
                    }

                candidates_by_day[day_number] = unique_places
                all_places.extend(unique_places)
                updated_days_info.append({**day_info, "hint_anchors": anchors_meta})

    # ── PostgreSQL upsert (전체 합산) ───────────────────────────────
    if all_places:
        try:
            await upsert_places(all_places)
        except Exception as e:
            warnings.append(f"DB upsert 실패: {type(e).__name__}: {e}")

    # days_info에 region/hint_anchors 채워서 user_input 업데이트
    updated_ui = {**ui, "days_info": updated_days_info}

    return {
        "user_input":        updated_ui,
        "candidates":        all_places,
        "candidates_by_day": candidates_by_day,
        "warnings":          warnings,
        "errors":            errors,
        "step":              "fetched",
    }