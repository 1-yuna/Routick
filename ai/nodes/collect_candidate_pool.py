# ─────────────────────────────────────────────────────────────────────
# collect_candidate_pool
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API로 raw 후보군 수집 + PostgreSQL 영구 저장
#
# 흐름:
#   1. day별 독립 호출
#      - 케이스 1 (only): radius 기반 원형 검색
#      - 케이스 2 (endpoint): rect 기반 사각형 검색
#   2. 좌표 → 행정구역명 변환 (region/startRegion/endRegion)
#      → days_info에 채워넣음
#   3. PostgreSQL upsert
# ─────────────────────────────────────────────────────────────────────

import asyncio
import httpx
import os

from utils.pool.kakao_search import (
    search_kakao_by_radius,
    search_kakao_by_rect,
    coord_to_region,
)
from utils.pool.db import upsert_places

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")


# ─── [노드] Kakao API + DB ───
async def collect_candidate_pool(state: dict) -> dict:
    ui       = state["user_input"]
    warnings: list[str] = []
    errors:   list[str] = []

    keywords   = ui.get("final_keywords") or []
    days_info  = ui.get("days_info") or []
    route_type = ui.get("route_type", "only")

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

    # ── 1. day별 독립 호출 ──────────────────────────────────────────
    async with httpx.AsyncClient(timeout=10.0) as client:
        for day_info in days_info:
            day_number = day_info["day_number"]
            day_places: list[dict] = []
            day_warnings: list[str] = []

            # 케이스 1: radius 검색
            if route_type == "only":
                lat       = day_info.get("center_lat")
                lng       = day_info.get("center_lng")
                radius_km = day_info.get("radius_km", 2.0)

                if lat is None or lng is None:
                    warnings.append(f"day{day_number} 좌표 없음 → 스킵")
                    continue

                day_places, day_warnings = await search_kakao_by_radius(
                    keywords=keywords,
                    lat=lat,
                    lng=lng,
                    radius_km=radius_km,
                )

                # ── 2. 좌표 → 지역명 변환 (only: region) ───────────
                region = await coord_to_region(client, lat, lng)
                day_info = {**day_info, "region": region}

            # 케이스 2: rect 검색
            elif route_type == "endpoint":
                rect_min_lat = day_info.get("rect_min_lat")
                rect_min_lng = day_info.get("rect_min_lng")
                rect_max_lat = day_info.get("rect_max_lat")
                rect_max_lng = day_info.get("rect_max_lng")

                if None in (rect_min_lat, rect_min_lng, rect_max_lat, rect_max_lng):
                    warnings.append(f"day{day_number} rect 좌표 없음 → 스킵")
                    continue

                day_places, day_warnings = await search_kakao_by_rect(
                    keywords=keywords,
                    rect_min_lat=rect_min_lat,
                    rect_min_lng=rect_min_lng,
                    rect_max_lat=rect_max_lat,
                    rect_max_lng=rect_max_lng,
                )

                # ── 2. 좌표 → 지역명 변환 (endpoint: start/end_region) ──
                # 원본 days에서 start/end 좌표 추출
                days_raw    = ui.get("days") or []
                day_raw     = next((d for d in days_raw if d["day_number"] == day_number), None)

                if day_raw:
                    start_region, end_region = await asyncio.gather(
                        coord_to_region(client, day_raw["start_lat"], day_raw["start_lng"]),
                        coord_to_region(client, day_raw["end_lat"],   day_raw["end_lng"]),
                    )
                    day_info = {**day_info, "start_region": start_region, "end_region": end_region}

            warnings.extend(day_warnings)

            # day별 중복 제거 (같은 place_id)
            seen: set[str] = set()
            unique_places: list[dict] = []
            for p in day_places:
                if p["id"] not in seen:
                    seen.add(p["id"])
                    unique_places.append(p)

            candidates_by_day[day_number] = unique_places
            all_places.extend(unique_places)
            updated_days_info.append(day_info)

            if not unique_places:
                warnings.append(f"day{day_number} 후보 0개")

    # ── 3. PostgreSQL upsert (전체 합산) ────────────────────────────
    if all_places:
        try:
            await upsert_places(all_places)
        except Exception as e:
            warnings.append(f"DB upsert 실패: {type(e).__name__}: {e}")

    # days_info에 region 채워서 user_input 업데이트
    updated_ui = {**ui, "days_info": updated_days_info}

    return {
        "user_input":        updated_ui,
        "candidates":        all_places,
        "candidates_by_day": candidates_by_day,
        "warnings":          warnings,
        "errors":            errors,
        "step":              "fetched",
    }