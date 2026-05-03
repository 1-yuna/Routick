# 스키마 정의
from typing import TypedDict, Annotated, Optional
import operator

# 타입 정의 - 입력
class UserInput(TypedDict):
    # 사용자 원본 입력
    # 장소(홍대역), 인원수, 연인, 혼성, 20대, 당일, [활기찬,힐링], [카페, 게임/보드게임]
    location: str
    party_size: int
    party_type: str
    genders: str
    age_group: str
    duration: str
    mood_preferences: list[str]
    activity_preferences: list[str]

    # 시간 관련 필드 (프론트에서 제공)
    # 2026-04-25, 10:00, 19:00, 8.0
    trip_date: str
    start_time: str
    end_time: str
    total_hours: float

    # [validate_input] 장소 정규화
    center_lat: Optional[float]
    center_lng: Optional[float]
    search_radius_km: Optional[float]

    # 식사 관련 필드
    needs_meal: Optional[bool]
    meal_times: Optional[list[str]]

    # validate_input에서 필수 키워드 추가
    final_keywords: Optional[list[str]]


# 타입 정의 - 후보(장소 하나의 기본 정보)
class Place(TypedDict):
    id: str
    name: str
    category: str
    lat: float
    lng: float
    tags: list[str]
    rating: float
    avg_stay_minutes: int
    open_hours: dict


# 타입 정의 - 후보(place의 점수 매기기)
class ScoredPlace(TypedDict):
    place: Place
    mood_score: float
    activity_score: float
    party_fit_score: float
    total_score: float


# 타입 정의 - 출력(ScoredPlace로 동선, 시간 배치)
class ItineraryItem(TypedDict):
    order: int
    place: Place
    arrive_at: str
    leave_at: str
    travel_to_next_minutes: int
    recommendation_reason: str


# 타입 정의 - 전체 state 설계도
class TravelState(TypedDict):
    # 입력
    user_input: UserInput

    # 넓게 수집된 raw 풀
    candidates: Annotated[list[Place], operator.add]

    # 거리/영업 필터링 + 거리 정보 추가된 풀
    filtered_candidates: list[Place]

    # 점수 & 필터링
    scored_candidates: list[ScoredPlace]
    shortlist: list[ScoredPlace]

    # 동선
    distance_matrix: list[list[float]]
    route: list[str]
    route_metrics: dict

    # 출력
    itinerary: list[ItineraryItem]
    rationale: str

    # 메타·제어
    errors: list[str]
    warnings: list[str]
    fallback_count: int
    retry_count: int
    step: str


# 초기화 함수 - 빈 state를 만들어줌
# 이후 로직: 초기화 함수를 받는 변수 = state. 함수들(노드)은 해당 state를 받아서 부분 수정함.

# 운영: 프론트에서 받은 진짜 user_input을 넣어서 호출
# 테스트: mocks.mock_user_input을 넣어서 호출
def make_initial_state(user_input: UserInput) -> TravelState:
    return {
        "user_input": user_input,
        "candidates": [],
        "filtered_candidates": [],
        "scored_candidates": [],
        "shortlist": [],
        "distance_matrix": [],
        "route": [],
        "route_metrics": {},
        "itinerary": [],
        "rationale": "",
        "errors": [],
        "warnings": [],
        "fallback_count": 0,
        "retry_count": 0,
        "step": "initialized",
    }