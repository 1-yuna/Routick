# ─────────────────────────────────────────────────────────────────────
# collect_candidate_pool
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API로 raw 후보군(~200개) 수집 + PostgreSQL 영구 저장
#
# 흐름:
#   1. Kakao API 호출 (kakao_search 호출)
#      - 현재 좌표로 검색
#      - 비동기 병렬, 일부 실패해도 진행
#   2. PostgreSQL upsert (db 사용)
#      - state.candidates와 별개로 DB에도 누적 저장
# ─────────────────────────────────────────────────────────────────────

from utils.pool.kakao_search import search_kakao_pool
from utils.pool.db import upsert_places


# ─── [노드] Kakao API + DB ───
async def collect_candidate_pool(state: dict) -> dict:
    # 필요한 입력 꺼내기
    ui = state["user_input"]
    warnings: list[str] = []
    errors: list[str] = []

    # 활동 키워드 결정
    keywords = ui.get("final_keywords") or ui.get("activity_preferences") or []
    if not keywords:
        warnings.append("activity_preferences 비어있음 → 기본 키워드 사용")
        keywords = ["맛집", "카페"]

    # 좌표 조회. 없으면 즉시 fail 리턴
    lat = ui.get("center_lat")
    lng = ui.get("center_lng")
    radius_km = ui.get("search_radius_km", 1.5)

    if lat is None or lng is None:
        errors.append("center_lat/center_lng 누락 — validate_input 점검 필요")
        return {
            "candidates": [],
            "errors": errors,
            "warnings": warnings,
            "step": "fetch_failed",
        }

    # Kakao api 호출 (비동기 병렬)
    places: list[dict] = []
    try:
        places, search_warnings, expanded = await search_kakao_pool(
            keywords=keywords,
            lat=lat,
            lng=lng,
            radius_km=radius_km,
            pages=3,
        )
        warnings.extend(search_warnings)
    except Exception as e:
        errors.append(f"kakao search 전체 실패: {type(e).__name__}: {e}")

    # PostgreSQL upsert (영구 저장)
    if places:
        try:
            await upsert_places(places)
        except Exception as e:
            warnings.append(f"DB upsert 실패: {type(e).__name__}: {e}")

    if not places:
        warnings.append("후보가 0개 — fallback/재시도 필요")

    return {
        "user_input": {**ui, "final_keywords": expanded},
        "candidates": places,
        "warnings": warnings,
        "errors": errors,
        "step": "fetched",
    }