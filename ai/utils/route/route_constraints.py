# ─────────────────────────────────────────────────────────────────────
# route_constraints
# ─────────────────────────────────────────────────────────────────────
# 동선 하나(6개 장소) 내부 제약 조건
#   - 카페 연속 배치 금지
#   - 동일 세부 카테고리 최대 1개
#   - 동일 장소·동일 브랜드 최대 1개
#   - 앵커 최소 1개 포함 (best-effort — 있으면 포함, 없으면 생략)
#
# day_filter.py와 로직 중복되지만, 동선 파일 그룹은 self-contained 유지
# (day 단위 제약과 route 단위 제약은 기준 범위가 다름 — day는 하루 전체 20~30개,
#  route는 동선 하나의 6개뿐이라 브랜드/카테고리 캡을 1개로 더 엄격하게 적용)
# ─────────────────────────────────────────────────────────────────────

import re

ROUTE_MAX_PER_BRAND    = 1
ROUTE_MAX_PER_CATEGORY = 1


# ─── 브랜드명 정규화 (지점 suffix 제거) ───
def brand_name(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r'\s+\S*(점|지점|호점|본점|직영점|분점)$', '', name)
    return name.strip()


# ─── 카테고리 상위 3단계 추출 ───
def category_prefix(category: str, depth: int = 3) -> str:
    parts = [p.strip() for p in (category or "").split(">")]
    return " > ".join(parts[:depth])


# ─── 후보가 브랜드 캡을 위반하는지 ───
def violates_brand_cap(place: dict, used_brands: set) -> bool:
    return brand_name(place.get("name", "")) in used_brands


# ─── 후보가 카테고리 캡을 위반하는지 ───
def violates_category_cap(place: dict, used_categories: set) -> bool:
    key = category_prefix(place.get("category", ""))
    return bool(key) and key in used_categories


# ─── 후보가 "카페 연속 배치 금지"를 위반하는지 ───
def violates_consecutive_cafe(place: dict, last_bucket: str | None) -> bool:
    return last_bucket == "cafe" and place.get("bucket") == "cafe"


# ─── 장소 하나를 동선에 반영할 때 브랜드/카테고리 사용 집합 갱신 ───
def register_place(place: dict, used_brands: set, used_categories: set) -> None:
    used_brands.add(brand_name(place.get("name", "")))
    key = category_prefix(place.get("category", ""))
    if key:
        used_categories.add(key)


# ─── 앵커 여부 (query_name 존재 = anchor_resolve에서 해소된 앵커) ───
def is_anchor(place: dict) -> bool:
    return bool(place.get("query_name"))