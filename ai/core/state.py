# ─────────────────────────────────────────────────────────────────────
# state
# ─────────────────────────────────────────────────────────────────────
# state 정의 (v4 — pipeline_redesign_v4.md 기준 전면 재작성)
#
# 흐름:
#   1. 초기 상태 생성 && 사용자 입력 저장
#   2. 입력 전처리 (preprocess_input)
#   3. 여행 권역 조회 (region_hint) — 신규 노드
#   4. 장소 수집 + 1차 필터링 (collect_and_filter_places)
#      - day당 30개로 축약, scored_by_day 롤백 재사용을 위해 유지
#   5. 장소 정보 보강 + 점수화 (enrich_and_score_places)
#      - day당 15개로 2차 필터링 (shortlist_by_day)
#   6. 동선 후보 생성 (generate_route_candidates)
#   7. 최적 일정 선택 (select_itinerary)
#      - GPT 요청 전 사전 검증 실패 시 6번 로직을 노드 내부에서 직접
#        재호출(quota 완화 15→30, 6→5슬롯) — 그래프 레벨 롤백 아님
#   8. 상세 정보 검증 + 응답 생성 (verify_and_respond)
#      - 대체 장소 탐색 실패 시 6번의 day 재생성 로직을 노드 내부에서
#        직접 재호출(day당 1회) — 이것도 그래프 레벨 롤백 아님
#
# 위 6번/8번 롤백이 전부 노드 내부 직접 재호출로 처리되기 때문에
# graph.py는 조건부 엣지 없는 단순 선형 그래프로 충분함
#
# 실제 배포 경로는 core/state.py (graph.py 등에서 `from core.state import ...`
# 로 임포트) — 이 프로젝트에서는 다른 노드/유틸 파일과 동일하게 평문 파일명으로
# 관리 (nodes.*, prompts.*, constants.* 파일들과 같은 컨벤션)
# ─────────────────────────────────────────────────────────────────────

from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator


# ─────────────────────────────────────────────────────────────────────
# Spring → AI 입력 구조
# ─────────────────────────────────────────────────────────────────────

class DayCoord(TypedDict):
    """케이스 2(endpoint)의 day별 좌표 + 장소명
    mid(경유지)는 선택 입력. 입력 시 출발지~경유지~도착지 순으로 동선 구성,
    미입력 시 직선 중간점으로 fallback."""
    day_number: int
    start_lat: float
    start_lng: float
    start_name: Optional[str]      # 프론트 카카오 자동완성에서 받은 장소명
    start_address: Optional[str]   # 출발지 주소
    start_place_id: Optional[str]  # 출발지 카카오 place_id
    mid_lat: Optional[float]       # 경유지 (선택)
    mid_lng: Optional[float]
    mid_name: Optional[str]
    end_lat: float
    end_lng: float
    end_name: Optional[str]        # 프론트 카카오 자동완성에서 받은 장소명
    end_address: Optional[str]     # 도착지 주소
    end_place_id: Optional[str]    # 도착지 카카오 place_id


class DayInfo(TypedDict):
    """day별 권역 정보 (region_hint에서 채움)"""
    day_number: int

    region_name: Optional[str]          # 기준 지역명
                                         # (only: destination 또는 역지오코딩 결과,
                                         #  endpoint: mid_name > start_name 또는 역지오코딩)
    region_concept: Optional[str]       # LLM이 제안한 하루 콘셉트
    region_reason: Optional[str]        # 그 권역을 고른 이유
    anchor_names: Optional[list[str]]   # LLM이 제안한 앵커 장소명 2~3개
                                         # (place_id/좌표 해소는 collect_and_filter_places에서)

    center_lat: Optional[float]         # 권역 기준 좌표
    center_lng: Optional[float]         # (only: destination/lat,lng 그대로,
                                         #  endpoint: mid 좌표 또는 start~end 직선 중간점)

    # endpoint 케이스 전용 — 실제 출발/도착 좌표 (동선 생성이 시작/끝 블록을 붙일 때 사용,
    # center와 별개로 그대로 실어 보냄)
    start_lat: Optional[float]
    start_lng: Optional[float]
    end_lat: Optional[float]
    end_lng: Optional[float]

    is_fallback: Optional[bool]         # 기준 지역명/좌표 확보 실패 또는 LLM 실패로
                                         # 반경 검색 폴백됐는지


class UserInput(TypedDict):
    # ── Spring에서 넘겨주는 값 ──────────────────────────────────────
    route_type: str                     # only / endpoint
    travel_days: int                    # 1=당일, 2=1박2일, 3=2박3일, 4=3박4일
    travel_date: str                    # "2025-06-15" (영업시간 체크용)
    transport: str                      # walk / car
    companion: str                      # solo/couple/friend/parents/children/pet
    moods: list[str]                    # ["active", "healing"] 등
    activities: list[str]               # ["nature/walk", "shopping"] 등
    avoid_activities: Optional[list[str]]

    # 케이스 1 (only) — 목적지 좌표 + 이름
    lat: Optional[float]
    lng: Optional[float]
    destination: Optional[str]          # 목적지 이름 (프론트 카카오 자동완성)
                                         # region_hint의 기준 지역명으로 우선 사용

    # 케이스 2 (endpoint) — day별 출발·도착 좌표
    days: Optional[list[DayCoord]]

    start_time: str                     # "09:00" (기본값)
    end_time: str                       # "22:00" (기본값)

    # ── preprocess_input 후 채워지는 값 ────────────────────────────
    companion_kr: Optional[str]         # 혼자/연인/친구/부모님과/자녀와/반려동물과
    moods_kr: Optional[list[str]]       # ["활기찬", "힐링"] 등
    activities_kr: Optional[list[str]]  # ["자연/산책", "쇼핑"] 등
    transport_kr: Optional[str]         # 도보 / 자동차
    duration_kr: Optional[str]          # 당일 / 1박2일 / 2박3일 / 3박4일
    travel_weekday: Optional[str]       # "월" / "화" / ... (영업시간 체크용)
    final_keywords: Optional[list[str]] # 검색 키워드 목록 (category + name 합산)
    name_search_keywords: Optional[list[str]]  # name 검색 전용 키워드

    # ── region_hint 후 채워지는 값 ─────────────────────────────────
    days_info: Optional[list[DayInfo]]


# ─────────────────────────────────────────────────────────────────────
# 파이프라인 내부 데이터
# ─────────────────────────────────────────────────────────────────────
# 장소(Place)/동선(Route) dict의 정확한 필드 구성은 그 값을 만드는 유틸 모듈이
# 기준임 (예: 장소 보강 필드는 utils/enrich_score/*.py, 동선 필드는
# utils/route/route_build.py) — 노드 함수들도 전부 plain dict로 주고받고 있어
# 여기서도 TypedDict로 다시 못박지 않고 느슨하게 dict로 둠

class TravelState(TypedDict):
    user_input: UserInput

    # 4. 장소 수집 + 1차 필터링 — day당 30개
    filtered_candidates: list[dict]
    filtered_by_day: dict[int, list[dict]]

    # 5. 장소 정보 보강 + 점수화
    scored_candidates: list[dict]              # 2차 필터링 이전 — day당 30개 전체 (점수 포함)
    scored_by_day: dict[int, list[dict]]        # ↑ day별 분리본
                                                 #   7번 사전 검증 실패 롤백 시 블로그/GPT 재호출 없이
                                                 #   quota만 다시 잘라 재사용
    shortlist: list[dict]                       # 2차 필터링 후 — day당 15개
    shortlist_by_day: dict[int, list[dict]]

    # 6. 동선 후보 생성 — route dict: {places, total_score, has_anchor, start_block, end_block}
    route_candidates_by_day: dict[int, list[dict]]
    route_candidates: list[dict]

    # 7. 최적 일정 선택
    final_itineraries: dict[int, dict]          # day_number → route dict 1개
    day_meta: dict[int, dict]                   # day_number → {select_reason}

    # 8. 상세 정보 검증 + 응답 생성
    response: dict                              # {transport, meta, days: [...]}

    # 메타·제어
    warnings: Annotated[list[str], operator.add]  # 노드마다 자기 몫만 반환 → 그래프가 누적
    step: str                                      # 마지막으로 완료된 단계 (덮어쓰기)


# ─────────────────────────────────────────────────────────────────────
# 초기화
# ─────────────────────────────────────────────────────────────────────

def make_initial_state(user_input: UserInput) -> TravelState:
    return {
        "user_input": user_input,

        "filtered_candidates": [],
        "filtered_by_day": {},

        "scored_candidates": [],
        "scored_by_day": {},
        "shortlist": [],
        "shortlist_by_day": {},

        "route_candidates_by_day": {},
        "route_candidates": [],

        "final_itineraries": {},
        "day_meta": {},

        "response": {},

        "warnings": [],
        "step": "initialized",
    }