# ─────────────────────────────────────────────────────────────────────
# collect_candidate_pool
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API로 raw 후보군 수집 + PostgreSQL 영구 저장
#
# 흐름:
#   1. final_keywords 기반 동의어 확장 (KEYWORD_EXPANSIONS)
#   2. Kakao API 병렬 호출
#   3. PostgreSQL upsert
# ─────────────────────────────────────────────────────────────────────

from utils.pool.kakao_search import search_kakao_pool
from utils.pool.db import upsert_places


# ─── [노드] Kakao API + DB ───
async def collect_candidate_pool(state: dict) -> dict:
    ui = state["user_input"]
    warnings: list[str] = []
    errors: list[str] = []

    # final_keywords 조회
    keywords = ui.get("final_keywords") or []
    if not keywords:
        warnings.append("final_keywords 비어있음 → 기본 키워드 사용")
        keywords = ["맛집", "카페"]

    # 좌표 조회
    lat = ui.get("center_lat")
    lng = ui.get("center_lng")
    radius_km = ui.get("search_radius_km", 1.0)

    if lat is None or lng is None:
        errors.append("center_lat/center_lng 누락 — preprocess_input 점검 필요")
        return {
            "candidates": [],
            "errors": errors,
            "warnings": warnings,
            "step": "fetch_failed",
        }

    # Kakao API 병렬 호출
    places: list[dict] = []
    expanded: list[str] = []
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

    # PostgreSQL upsert
    if places:
        try:
            await upsert_places(places)
        except Exception as e:
            warnings.append(f"DB upsert 실패: {type(e).__name__}: {e}")

    if not places:
        warnings.append("후보가 0개")

    return {
        "user_input": {**ui, "final_keywords": expanded},
        "candidates": places,
        "warnings": warnings,
        "errors": errors,
        "step": "fetched",
    }