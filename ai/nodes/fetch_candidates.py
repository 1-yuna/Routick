# ─────────────────────────────────────────────────────────────────────
# fetch_candidates
# ─────────────────────────────────────────────────────────────────────
# Kakao Local API로 raw 후보군(~200개) 수집 + PostgreSQL 영구 저장
#
# 흐름:
#   1. state에서 검색 키워드/좌표 꺼내기
#   2. Kakao API 호출 (utils/kakao_search.py 사용)
#      - 비동기 병렬, 일부 실패해도 진행
#   3. PostgreSQL upsert (utils/db.py 사용)
#      - state.candidates와 별개로 마스터 DB에도 누적 저장
#   4. state.candidates 채워서 다음 노드로 전달
#
# ─────────────────────────────────────────────────────────────────────


from utils.kakao_search import search_kakao_pool
from utils.db import upsert_places


async def fetch_candidates(state: dict) -> dict:
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
        places, search_warnings = await search_kakao_pool(
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

    # state에 저장 (다음 노드로 전달)
    return {
        "candidates": places,
        "warnings": warnings,
        "errors": errors,
        "step": "fetched",
    }