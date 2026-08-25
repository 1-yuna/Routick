# ─────────────────────────────────────────────────────────────────────
# anchor_resolve
# ─────────────────────────────────────────────────────────────────────
# 앵커 이름 → place_id/좌표/카테고리 해소
# ─────────────────────────────────────────────────────────────────────

import re

import httpx

from utils.collect_filter.day_collect import kakao_keyword_search_radius, parse_kakao_doc

MAX_ANCHORS = 3


# ─── 앵커 이름 → place_id/좌표/카테고리 해소 ───
async def resolve_anchors(
    client: httpx.AsyncClient,
    anchor_names: list[str],
    lat: float,
    lng: float,
    radius_km: float,
    avoid_place_ids: set[str],
) -> list[dict]:
    radius_m = min(int(radius_km * 1000), 20000)
    resolved = []
    for name in anchor_names[:MAX_ANCHORS]:
        try:
            docs = await kakao_keyword_search_radius(client, name, lat, lng, radius_m, page=1)
        except Exception:
            continue
        if not docs:
            stripped = re.sub(r"\s*\([^)]*\)", "", name).strip()
            if not stripped or stripped == name:
                continue
            try:
                docs = await kakao_keyword_search_radius(client, stripped, lat, lng, radius_m, page=1)
            except Exception:
                continue
            if not docs:
                continue
        place = parse_kakao_doc(docs[0])
        if place["id"] in avoid_place_ids:
            continue
        resolved.append({
            **place,
            "place_id":   place["id"],
            "query_name": name,
        })
    return resolved