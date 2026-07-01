# ─────────────────────────────────────────────────────────────────────
# mocks
# ─────────────────────────────────────────────────────────────────────
# 개발/테스트용 mock 데이터만
# ─────────────────────────────────────────────────────────────────────

from core.state import UserInput


# ─── 케이스 1: 목적지만 (only) ───
mock_user_input_only: UserInput = {
    # Spring에서 넘겨주는 값
    "route_type":       "only",
    "travel_days":      2,
    "travel_date":      "2025-06-15",
    "transport":        "walk",
    "companion":        "couple",
    "moods":            ["active", "healing", "clean"],
    "activities":       ["activity", "nature"],
    "avoid_activities": ["노래"],
    "lat":              37.5572,
    "lng":              126.9245,
    "days":             None,
    "start_time":       "11:00",
    "end_time":         "22:00",

    # [preprocess_input] 내부 변환 후 채워지는 값
    "companion_kr":          None,
    "moods_kr":              None,
    "activities_kr":         None,
    "transport_kr":          None,
    "duration_kr":           None,
    "travel_weekday":        None,
    "final_keywords":        None,
    "name_search_keywords":  None,
    "days_info":             None,
}


# ─── 케이스 2: 출발·도착 (endpoint) ───
# day1: 해운대역 → 코오롱씨클라우드호텔
# day2: 코오롱씨클라우드호텔 → 코오롱씨클라우드호텔 (광안리 경유)
mock_user_input_endpoint: UserInput = {
    # Spring에서 넘겨주는 값
    "route_type":       "endpoint",
    "travel_days":      2,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "active"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              None,
    "lng":              None,
    "days": [
        {
            "day_number":     1,
            "start_lat":      35.1631, "start_lng": 129.1637,
            "start_name":     "해운대역",
            "start_address":  "부산 해운대구 중동 1428",
            "start_place_id": "8362476",
            "mid_lat":        35.1587, "mid_lng": 129.1604,
            "mid_name":       "해운대",
            "end_lat":        35.1602, "end_lng": 129.1607,
            "end_name":       "코오롱씨클라우드호텔",
            "end_address":    "부산 해운대구 우동 1408-5",
            "end_place_id":   "11819137",
        },
        {
            "day_number":     2,
            "start_lat":      35.1602, "start_lng": 129.1607,
            "start_name":     "코오롱씨클라우드호텔",
            "start_address":  "부산 해운대구 우동 1408-5",
            "start_place_id": "11819137",
            "mid_lat":        35.1531, "mid_lng": 129.1186,
            "mid_name":       "광안리",
            "end_lat":        35.1602, "end_lng": 129.1607,
            "end_name":       "코오롱씨클라우드호텔",
            "end_address":    "부산 해운대구 우동 1408-5",
            "end_place_id":   "11819137",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",

    # [preprocess_input] 내부 변환 후 채워지는 값
    "companion_kr":          None,
    "moods_kr":              None,
    "activities_kr":         None,
    "transport_kr":          None,
    "duration_kr":           None,
    "travel_weekday":        None,
    "final_keywords":        None,
    "name_search_keywords":  None,
    "days_info":             None,
}