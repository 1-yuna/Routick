# mocks.py — 개발/테스트용 mock 데이터만
from state import UserInput

# mock - user_input
mock_user_input: UserInput = {
    "location": "홍대역",
    "party_size": 2,
    "party_type": "연인",
    "genders": "혼성",
    "age_group": "20대",
    "duration": "당일",
    "mood_preferences": ["활기찬", "힐링", "이색"],
    "activity_preferences": ["카페", "게임/보드게임", "동물 체험", "액티비티"],

    "trip_date": "2026-04-24",
    "start_time": "10:00",
    "end_time": "19:00",
    "total_hours": 8.0,

    "center_lat": None,
    "center_lng": None,
    "search_radius_km": None,

    "needs_meal": None,
    "meal_times": None,
    "final_keywords": None,
}