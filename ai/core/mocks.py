# ─────────────────────────────────────────────────────────────────────
# mocks
# ─────────────────────────────────────────────────────────────────────
# 개발/테스트용 mock 데이터만
# ─────────────────────────────────────────────────────────────────────

from core.state import UserInput


# ─── 사용자 mock 데이터 ───
mock_user_input: UserInput = {
    # Spring에서 넘겨주는 값
    "destination": "해운대역",
    "lat": 35.1631,
    "lng": 129.1635,
    "travel_days": 2,
    "companion": "couple",
    "age_group": "20s",
    "moods": ["active", "healing"],
    "activities": ["nature/walk", "shopping"],
    "transport": "walk",
    "avoid_activities": [],
    "start_time": "09:00",
    "end_time": "22:00",

    # [preprocess_input] 내부 변환 후 채워지는 값
    "center_lat": None,
    "center_lng": None,
    "search_radius_km": None,
    "final_keywords": None,
    "companion_kr": None,
    "age_group_kr": None,
    "moods_kr": None,
    "activities_kr": None,
    "transport_kr": None,
    "duration_kr": None,
}