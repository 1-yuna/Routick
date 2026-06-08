# ─────────────────────────────────────────────────────────────────────
# state
# ─────────────────────────────────────────────────────────────────────
# state 정의
#
# 흐름:
#   1. 초기 상태 생성 && 사용자 입력 저장
#      - UserInput을 기반으로 TravelState 구조 생성
#   2. 후보 수집 (candidates 생성)
#      - Kakao API 기반 장소 검색
#   3. 1차 필터링 (filtered_candidates 생성)
#      - travel_days 기반 동적 cap으로 축약
#   4. 2차 필터링 (scored_candidates 생성, shortlist 생성)
#      - 점수화 + travel_days 기반 shortlist 구성
#   5. 이동시간 행렬 계산 (travel_matrix)
#   6. 일정 계획 리스트 작성 (plan_itinerary)
#      - N개 동선 생성 + 기본 예외처리
#   7. 최적 일정 선택 (select_itinerary)
#      - LLM이 최적 동선 선택 + 추천 이유 생성
#   8. 응답 생성 (generate_response)
# ─────────────────────────────────────────────────────────────────────

from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator


# ─── 사용자 원본 입력 ───
class UserInput(TypedDict):
    # Spring에서 넘겨주는 값
    destination: str
    lat: float
    lng: float
    travel_days: int            # 1=당일, 2=1박2일, 3=2박3일, 4=3박4일
    companion: str              # solo/couple/friend/parents/children/pet
    age_group: str              # 10s/20s/30s/40s/50plus
    moods: list[str]            # ["active", "healing"] 등
    activities: list[str]       # ["nature/walk", "shopping"] 등
    transport: str              # walk/car
    avoid_activities: Optional[list[str]]
    start_time: str             # "09:00" (기본값)
    end_time: str               # "22:00" (기본값)

    # [preprocess_input] 내부 변환 후 채워지는 값
    center_lat: Optional[float]
    center_lng: Optional[float]
    search_radius_km: Optional[float]
    final_keywords: Optional[list[str]]

    # 내부 변환값 (한국어)
    companion_kr: Optional[str]     # 혼자/연인/친구/부모님과/자녀와/반려동물과
    age_group_kr: Optional[str]     # 10대/20대/30대/40대/50대
    moods_kr: Optional[list[str]]   # ["활기찬", "힐링"] 등
    activities_kr: Optional[list[str]]  # ["자연/산책", "쇼핑"] 등
    transport_kr: Optional[str]     # 도보/자동차
    duration_kr: Optional[str]      # 당일/1박2일/2박3일/3박4일


# ─── [타입 정의] 장소 ───
class Place(TypedDict):
    id: str
    name: str
    category: str
    category_group_code: str
    lat: float
    lng: float
    phone: str
    address_name: str
    road_address_name: str
    place_url: str
    tags: list[str]
    avg_stay_minutes: int

    # [second_filter] LLM 보강 후 채워지는 값
    bucket: str                 # cafe/food/activity/lodging/other
    atmosphere: list[str]       # ["활기찬", "힐링"] 등
    best_for: list[str]         # ["연인", "친구"] 등
    place_tags: list[str]       # ["카페", "바다"] 등
    revisit_intent: str         # high/medium/low
    summary: str                # 한줄 요약


# ─── [타입 정의] 장소 + 점수 ───
class ScoredPlace(TypedDict):
    place: Place
    mood_score: float
    activity_score: float
    party_fit_score: float
    revisit_score: float
    total_score: float


# ─── [타입 정의] 일정 아이템 ───
class ItineraryItem(TypedDict):
    order: int
    place: Place
    arrive_at: str
    leave_at: str
    travel_to_next_minutes: int
    recommendation_reason: str


# ─── 전체 state 설계도 ───
class TravelState(TypedDict):
    # 사용자 입력
    user_input: UserInput

    # 후보 수집
    candidates: Annotated[list[Place], operator.add]

    # 1차 필터링 (travel_days 기반 동적 cap)
    filtered_candidates: list[Place]

    # 2차 필터링 (점수화 + shortlist)
    scored_candidates: list[ScoredPlace]
    shortlist: list[ScoredPlace]

    # 이동시간 행렬
    distance_matrix: list[list[float]]  # km 단위 거리
    time_matrix: list[list[float]]      # 분 단위 이동시간
    place_index: list[str]              # 인덱스 → place_id 매핑

    # 일정 계획
    itineraries: list[list[ItineraryItem]]      # N개 동선 리스트
    selected_itinerary: list[ItineraryItem]     # 최종 선택된 동선

    # 메타·제어
    errors: list[str]
    warnings: list[str]
    retry_count: int
    step: str


# ─── 초기화 함수 ───
def make_initial_state(user_input: UserInput) -> TravelState:
    return {
        "user_input": user_input,
        "candidates": [],
        "filtered_candidates": [],
        "scored_candidates": [],
        "shortlist": [],
        "distance_matrix": [],
        "time_matrix": [],
        "place_index": [],
        "itineraries": [],
        "selected_itinerary": [],
        "errors": [],
        "warnings": [],
        "retry_count": 0,
        "step": "initialized",
    }