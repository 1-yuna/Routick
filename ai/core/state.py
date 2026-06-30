# ─────────────────────────────────────────────────────────────────────
# state
# ─────────────────────────────────────────────────────────────────────
# state 정의
#
# 흐름:
#   1. 초기 상태 생성 && 사용자 입력 저장
#   2. 전처리 (preprocess_input)
#      - route_type에 따라 day별 좌표/반경/지역명 계산
#   3. 후보 수집 (collect_candidate_pool)
#      - day별 독립 수집 (only: 원형 radius / endpoint: rect)
#   4. 1차 필터링 (first_filter_candidates)
#   5. 2차 필터링 (second_filter_candidates)
#      - 블로그 보강 + 점수 계산 + shortlist 구성
#   6. 이동시간 행렬 계산 (travel_matrix)
#      - day별 독립 계산
#   7. 동선 후보 생성 + 일정 계획 (plan_itinerary)
#      - parking 거점 추가 (transport=car)
#      - fallback 처리
#   8. 최적 일정 선택 (select_itinerary)
#      - LLM 선택 + rollback 처리
#   9. 최종 정보 보충 (fetch_details)
#      - 구글 Places API (이미지/별점/리뷰수/영업시간)
#      - 영업시간 충돌 시 대체 장소 교체
#  10. 응답 생성 (generate_response)
#      - blocks 배열 구성 (place/walk/parking 타입 혼합)
# ─────────────────────────────────────────────────────────────────────

from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator


# ─────────────────────────────────────────────────────────────────────
# Spring → AI 입력 구조
# ─────────────────────────────────────────────────────────────────────

class DayCoord(TypedDict):
    """케이스 2(endpoint)의 day별 좌표 + 장소명"""
    day_number: int
    start_lat: float
    start_lng: float
    start_name: Optional[str]   # 프론트 카카오 자동완성에서 받은 장소명
    end_lat: float
    end_lng: float
    end_name: Optional[str]     # 프론트 카카오 자동완성에서 받은 장소명


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

    # 케이스 1 (only) — 목적지 좌표
    lat: Optional[float]
    lng: Optional[float]

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

    # day별 검색 파라미터 (preprocess_input에서 계산)
    days_info: Optional[list["DayInfo"]]


class DayInfo(TypedDict):
    """day별 검색 파라미터 (preprocess_input에서 계산)"""
    day_number: int

    # 케이스 1: 원형 반경
    center_lat: Optional[float]
    center_lng: Optional[float]
    radius_km: Optional[float]

    # 케이스 2: 사각형 영역
    rect_min_lat: Optional[float]
    rect_min_lng: Optional[float]
    rect_max_lat: Optional[float]
    rect_max_lng: Optional[float]

    # 지역명 (collect_candidate_pool에서 카카오 좌표→행정구역 API로 채움)
    region: Optional[str]           # 케이스 1: 목적지 지역명
    start_region: Optional[str]     # 케이스 2: 시작 지역명
    end_region: Optional[str]       # 케이스 2: 도착 지역명


# ─────────────────────────────────────────────────────────────────────
# 장소 관련 타입
# ─────────────────────────────────────────────────────────────────────

class Place(TypedDict):
    """카카오 API로 수집한 장소 원본 + 보강 필드"""
    id: str
    name: str
    category: str
    category_group_code: str
    phone: str
    address_name: str
    road_address_name: str
    lat: float
    lng: float
    place_url: str

    # ── second_filter (LLM 보강) 후 채워지는 값 ────────────────────
    atmosphere: list[str]           # ["활기찬", "힐링"] 등
    best_for: list[str]             # ["연인", "친구"] 등
    place_tags: list[str]           # ["산책로", "한식"] 등
    revisit_intent: str             # high / medium / low
    summary: str                    # 한줄 요약 (30자 이내)

    # ── generate_candidates (버킷 분류) 후 채워지는 값 ─────────────
    bucket: str                     # food / cafe / activity / browse / pop / parking

    # ── fetch_details (구글 Places API) 후 채워지는 값 ─────────────
    src: Optional[str]              # 대표 이미지 URL
    status: Optional[str]           # 영업 상태 ("영업 중" / "영업 종료" 등)


class ScoredPlace(TypedDict):
    """점수가 계산된 장소"""
    place: Place
    mood_score: float
    party_fit_score: int
    revisit_score: int
    blog_score: int                 # v2 신규
    total_score: float


# ─────────────────────────────────────────────────────────────────────
# 일정 관련 타입
# ─────────────────────────────────────────────────────────────────────

class Transport(TypedDict):
    """이동 정보"""
    mode: str       # walk / car
    minutes: int    # 이동 시간 (분)


class ParkingBlock(TypedDict):
    """주차장 블록"""
    type: str                           # "parking"
    bucket: str                         # "parking"
    name: str
    address: str
    lat: float
    lng: float
    description: Optional[str]          # 주차 요금 정보
    enter_transport: Optional[Transport] # 이전 블록 → 주차장 (이전이 parking이면 없음)
    exit_transport: Optional[Transport]  # 주차장 → 다음 블록


class StartEndPoint(TypedDict):
    """출발지/도착지 정보 (endpoint 케이스만)"""
    name: str
    address: str
    lat: float
    lng: float
    place_id: str
    exit_transport: Optional[Transport]   # 출발지 → 첫 블록 (start용)
    enter_transport: Optional[Transport]  # 마지막 블록 → 도착지 (end용)


class ItineraryItem(TypedDict):
    """동선 내 장소 아이템 (plan_itinerary에서 생성)"""
    order: int
    place: Place
    arrive_at: str
    leave_at: str
    travel_to_next_minutes: int
    recommendation_reason: str          # select_itinerary에서 채워짐


class DayItinerary(TypedDict):
    """day별 확정 동선"""
    day_number: int
    itinerary: list[ItineraryItem]
    parking_blocks: list[ParkingBlock]  # transport=car일 때만 (plan_itinerary에서 추가)
    start: Optional[StartEndPoint]      # 출발지 (endpoint 케이스만)
    end: Optional[StartEndPoint]        # 도착지 (endpoint 케이스만)


# ─────────────────────────────────────────────────────────────────────
# 전체 state
# ─────────────────────────────────────────────────────────────────────

class TravelState(TypedDict):
    # 사용자 입력
    user_input: UserInput

    # 후보 수집 (day별로 분리, day_number 키)
    candidates: Annotated[list[Place], operator.add]            # 전체 합산 (LangGraph reducer)
    candidates_by_day: dict[int, list[Place]]                   # day별 분리본

    # 1차 필터링
    filtered_candidates: list[Place]
    filtered_by_day: dict[int, list[Place]]                     # day별 분리본

    # 2차 필터링
    scored_candidates: list[ScoredPlace]
    shortlist: list[ScoredPlace]
    shortlist_by_day: dict[int, list[ScoredPlace]]              # day별 분리본

    # 이동시간 행렬 (day별) - generate_candidates에서 계산
    distance_matrix_by_day: dict[int, list[list[float]]]
    time_matrix_by_day: dict[int, list[list[float]]]
    place_index_by_day: dict[int, list[str]]                    # day별 인덱스 → place_id

    # 동선 후보 (generate_candidates에서 생성)
    all_routes_by_day: dict[int, list[dict]]                    # day별 전체 동선
    valid_routes_by_day: dict[int, list[dict]]                  # day별 유효 동선
    invalid_routes_by_day: dict[int, list[dict]]                # day별 제외된 동선

    # 일정 후보 (plan_itinerary에서 상위 5개 추출)
    itineraries_by_day: dict[int, list[list[ItineraryItem]]]    # day별 후보 동선들

    # 최종 선택된 동선 (day별)
    selected_itinerary: list[DayItinerary]

    # rollback 제어
    excluded_place_ids: list[str]                               # select_itinerary rollback 시 전달
    retry_count: int

    # 메타·제어
    errors: list[str]
    warnings: list[str]
    step: str

    # 최종 응답
    response: dict


# ─────────────────────────────────────────────────────────────────────
# 초기화
# ─────────────────────────────────────────────────────────────────────

def make_initial_state(user_input: UserInput) -> TravelState:
    return {
        "user_input": user_input,

        "candidates": [],
        "candidates_by_day": {},

        "filtered_candidates": [],
        "filtered_by_day": {},

        "scored_candidates": [],
        "shortlist": [],
        "shortlist_by_day": {},

        "distance_matrix_by_day": {},
        "time_matrix_by_day": {},
        "place_index_by_day": {},

        "all_routes_by_day": {},
        "valid_routes_by_day": {},
        "invalid_routes_by_day": {},

        "itineraries_by_day": {},

        "selected_itinerary": [],

        "excluded_place_ids": [],
        "retry_count": 0,

        "errors": [],
        "warnings": [],
        "step": "initialized",

        "response": {},
    }