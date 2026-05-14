# ─────────────────────────────────────────────────────────────────────
# make_initial_state
# ─────────────────────────────────────────────────────────────────────
# state 정의
#
# 흐름:
#   1. 초기 상태 생성 && 사용자 입력 저장
#      -  UserInput을 기반으로 TravelState 구조 생성
#   2. 후보 수집 (candidates 생성)
#      - Kakao API 기반 장소 검색
#   3. 1차 필터링 (filtered_candidates 생성)
#      - 50개로 필터
#   4. 2차 필터링 (scored_candidates 생성, shortlist 생성)
#      - 점수화
#      - 30개로 필터
#
# TODO: 장소 간 거리, 동선 최적화, 시간 기반? 등등
#
# ─────────────────────────────────────────────────────────────────────

from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator


#  ─── 사용자 원본 입력 ───
class UserInput(TypedDict):
    location: str
    party_size: int
    party_type: str
    genders: str
    age_group: str
    duration: str
    mood_preferences: list[str]
    activity_preferences: list[str]
    dislike_keywords: Optional[list[str]]

    # 2026-04-25
    trip_date: str

    # [validate_input] 장소 정규화
    center_lat: Optional[float]
    center_lng: Optional[float]
    search_radius_km: Optional[float]

    # [validate_input] 활동 키워드 보강
    final_keywords: Optional[list[str]]

    # TODO: 우선, 도보로 작성
    # [travel_matrix] 이동수단 + 여행 시간
    transport_mode: str  # "도보" | "자전거" | "자동차"
    start_time: str  # "09:00" - default로 작성
    end_time: str  # "21:00" - default로 작성


#  ─── [타입 정의] 장소 ───
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

    bucket: str
    atmosphere: list[str]
    best_for: list[str]
    place_tags: list[str]
    revisit_intent: str
    summary: str


#  ─── [타입 정의] 장소 + 점수 ───
class ScoredPlace(TypedDict):
    place: Place
    mood_score: float
    activity_score: float
    party_fit_score: float
    revisit_score: float
    total_score: float


# TODO: 아직 안함
#  ─── [타입 정의] 출력 ───
class ItineraryItem(TypedDict):
    order: int
    place: Place
    arrive_at: str
    leave_at: str
    travel_to_next_minutes: int
    recommendation_reason: str


#  ─── 전체 state 설계도 ───
class TravelState(TypedDict):
    # 사용자 입력
    user_input: UserInput

    # 전체 pool
    candidates: Annotated[list[Place], operator.add]

    # 1차 필터 - 50개
    filtered_candidates: list[Place]

    # 2차 필터
    # 점수화(50개), 필터화(30개)
    scored_candidates: list[ScoredPlace]
    shortlist: list[ScoredPlace]

    # [travel_matrix] 이동시간 행렬
    distance_matrix: list[list[float]] # km 단위 거리
    time_matrix: list[list[float]]  # 분 단위 이동시간
    place_index: list[str]  # 인덱스 → place_id 매핑
    route: list[str]
    route_metrics: dict

    # TODO: 앞으로 할 것
    # 출력
    itinerary: list[ItineraryItem]
    rationale: str

    # 메타·제어
    errors: list[str]
    warnings: list[str]
    fallback_count: int
    retry_count: int
    step: str


#  ─── 초기화 함수 ───
def make_initial_state(user_input: UserInput) -> TravelState:
    # activity_preferences 기본값 보정
    if not user_input.get("activity_preferences"):
        user_input["activity_preferences"] = ["맛집"]
    else:
        if "맛집" not in user_input["activity_preferences"]:
            user_input["activity_preferences"].append("맛집")

    return {
        "user_input": user_input,
        "candidates": [],
        "filtered_candidates": [],
        "scored_candidates": [],
        "shortlist": [],
        "distance_matrix": [],
        "time_matrix": [],
        "place_index": [],
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