# ─────────────────────────────────────────────────────────────────────
# validate_routes
# ─────────────────────────────────────────────────────────────────────
# GPT 요청 전 검증
#   - 전체 여행 시간(start_time~end_time) 안에 일정 완료
#   - 동선 안에 장소 및 동일 브랜드 중복 없음
#   - 지정한 카테고리 순서 충족 (슬롯 패턴 + 카페 연속 배치 금지)
#   - 앵커 장소 최소 1개 포함
#
# route_build.py가 생성 시점에 이미 대부분 지키도록 만들어두긴 했지만,
# 이 노드는 "생성 결과를 신뢰하지 않고 다시 검증"하는 게 목적이라 독립적으로 재검사함
# (route_build.py 로직이 바뀌어도 이 노드가 계속 안전하게 걸러내도록)
# ─────────────────────────────────────────────────────────────────────

from utils.route.route_build import SLOT_PATTERN_5, SLOT_PATTERN_6
from utils.route.route_constraints import brand_name
from utils.route.route_timing import stay_minutes

PATTERNS_BY_LENGTH = {len(SLOT_PATTERN_6): SLOT_PATTERN_6, len(SLOT_PATTERN_5): SLOT_PATTERN_5}


# ─── "HH:MM" → 자정 기준 분 ───
def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# ─── 하루 이동+체류 총 소요시간(분) ───
def _total_minutes(route: dict) -> int:
    total = sum(leg["minutes"] for leg in route["legs"])
    total += sum(stay_minutes(p) for p in route["places"])
    if route.get("start_block"):
        total += route["start_block"]["travel_to_first"]["minutes"]
    if route.get("end_block"):
        total += route["end_block"]["travel_from_last"]["minutes"]
    return round(total)


# ─── 카테고리 순서(슬롯 패턴) + 카페 연속 배치 금지 확인 ───
def _check_slot_order(places: list[dict]) -> str | None:
    pattern = PATTERNS_BY_LENGTH.get(len(places))
    if pattern is None:
        return f"알 수 없는 슬롯 길이({len(places)})"

    last_bucket = None
    for i, p in enumerate(places):
        slot_type = pattern[i]
        bucket = p.get("bucket")
        if slot_type == "food" and bucket != "food":
            return f"{i + 1}번 슬롯은 밥이어야 하는데 {bucket}"
        if slot_type == "flex" and bucket not in ("cafe", "activity"):
            return f"{i + 1}번 슬롯은 카페/활동이어야 하는데 {bucket}"
        if bucket == "cafe" and last_bucket == "cafe":
            return f"{i}번, {i + 1}번 슬롯 카페 연속 배치"
        last_bucket = bucket
    return None


# ─── 동선 안 장소/브랜드 중복 확인 ───
def _check_no_duplicates(places: list[dict]) -> str | None:
    ids = [p["id"] for p in places]
    if len(ids) != len(set(ids)):
        return "동일 장소 중복"
    brands = [brand_name(p.get("name", "")) for p in places]
    if len(brands) != len(set(brands)):
        return "동일 브랜드 중복"
    return None


# ─── 앵커 최소 1개 포함 확인 ───
def _check_anchor(places: list[dict]) -> str | None:
    if not any(p.get("query_name") for p in places):
        return "앵커 없음"
    return None


# ─── 동선 하나 검증 — 통과하면 None, 실패하면 사유 문자열 ───
def validate_route(route: dict, budget_minutes: int) -> str | None:
    places = route["places"]

    reason = _check_no_duplicates(places)
    if reason:
        return reason
    reason = _check_slot_order(places)
    if reason:
        return reason
    reason = _check_anchor(places)
    if reason:
        return reason

    total = _total_minutes(route)
    if total > budget_minutes:
        return f"시간 초과 ({total}분 > {budget_minutes}분)"

    return None


# ─── 실패 사유가 "이 동선에 쓰인 특정 장소들 탓"인지 판단 ───
# 시간 초과는 동선 전체(6개 조합)의 구조적 문제라 특정 장소 탓으로 보기 어렵고,
# day 후보들이 서로 장소를 많이 공유하는 상황에서 시간 초과 동선의 장소를 전부
# 제외 목록에 넣으면 재생성용 풀이 통째로 비어버릴 수 있음(실측 확인함) —
# 그래서 시간 초과는 제외 대상에서 뺌 (6→5슬롯 축소만으로 대응)
def _is_place_attributable(reason: str) -> bool:
    return not reason.startswith("시간 초과")


# ─── day 하나: 후보 동선들을 검증해서 (유효 동선, 실패 사유 목록, 실패 장소 id 집합)으로 분리 ───
def validate_day_routes(routes: list[dict], budget_minutes: int) -> tuple[list[dict], list[str], set[str]]:
    valid: list[dict] = []
    reasons: list[str] = []
    failed_place_ids: set[str] = set()

    for route in routes:
        reason = validate_route(route, budget_minutes)
        if reason is None:
            valid.append(route)
        else:
            reasons.append(reason)
            if _is_place_attributable(reason):
                failed_place_ids.update(p["id"] for p in route["places"])

    return valid, reasons, failed_place_ids


# ─── 여행 시간 예산(분) — ui의 start_time/end_time 기준 ───
def trip_budget_minutes(ui: dict) -> int:
    start = ui.get("start_time", "11:00")
    end   = ui.get("end_time", "22:00")
    return max(0, _to_minutes(end) - _to_minutes(start))