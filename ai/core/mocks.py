# ─────────────────────────────────────────────────────────────────────
# mocks
# ─────────────────────────────────────────────────────────────────────
# 개발/테스트용 mock 데이터만
# ─────────────────────────────────────────────────────────────────────

from core.state import UserInput


# ─── 사용자 mock 데이터 ───
mock_user_input: UserInput = {
    "location": "해운대역",
    "party_size": 2,
    "party_type": "연인",
    "genders": "혼성",
    "age_group": "20대",
    "duration": "당일",
    "mood_preferences": ["활기찬", "힐링", "이색"],
    "activity_preferences": ["카페", "게임/보드게임", "동물체험", "액티비티","바다","이색체험"],
    "dislike_keywords": [ "PC" ,"술집"],

    "trip_date": "2026-04-24",

    "center_lat": None,
    "center_lng": None,
    "search_radius_km": None,

    "final_keywords": None,

    "transport_mode": "도보",
}