# ─────────────────────────────────────────────────────────────────────
# mocks
# ─────────────────────────────────────────────────────────────────────
# 개발/테스트용 mock 데이터 (9개 케이스)
# ─────────────────────────────────────────────────────────────────────

from core.state import UserInput


# ══════════════════════════════════════════════════════════════════════
# 케이스 1: 목적지 + 당일 + 도보
# ══════════════════════════════════════════════════════════════════════
mock_only_1day_walk: UserInput = {
    "route_type":       "only",
    "travel_days":      1,
    "travel_date":      "2025-06-15",
    "transport":        "walk",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              37.5572,
    "lng":              126.9245,
    "days":             None,
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 2: 목적지 + 당일 + 자동차
# ══════════════════════════════════════════════════════════════════════
mock_only_1day_car: UserInput = {
    "route_type":       "only",
    "travel_days":      1,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              37.5572,
    "lng":              126.9245,
    "days":             None,
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 3: 목적지 + 2박3일 + 도보
# ══════════════════════════════════════════════════════════════════════
mock_only_3day_walk: UserInput = {
    "route_type":       "only",
    "travel_days":      3,
    "travel_date":      "2025-06-15",
    "transport":        "walk",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              37.5572,
    "lng":              126.9245,
    "days":             None,
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 4: 목적지 + 2박3일 + 자동차
# ══════════════════════════════════════════════════════════════════════
mock_only_3day_car: UserInput = {
    "route_type":       "only",
    "travel_days":      3,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
    "activities":       ["activity", "nature"],
    "avoid_activities": [],
    "lat":              37.5572,
    "lng":              126.9245,
    "days":             None,
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 5: 출발/도착 + 당일 + 도보
# 해운대역 → 해운대해수욕장
# ══════════════════════════════════════════════════════════════════════
mock_endpoint_1day_walk: UserInput = {
    "route_type":       "endpoint",
    "travel_days":      1,
    "travel_date":      "2025-06-15",
    "transport":        "walk",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
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
            "end_lat":        35.1585, "end_lng": 129.1599,
            "end_name":       "해운대해수욕장",
            "end_address":    "부산 해운대구 우동",
            "end_place_id":   "7913306",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 6: 출발/도착 + 당일 + 자동차
# 해운대역 → 해운대해수욕장
# ══════════════════════════════════════════════════════════════════════
mock_endpoint_1day_car: UserInput = {
    "route_type":       "endpoint",
    "travel_days":      1,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
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
            "end_lat":        35.1585, "end_lng": 129.1599,
            "end_name":       "해운대해수욕장",
            "end_address":    "부산 해운대구 우동",
            "end_place_id":   "7913306",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 7: 출발/도착 + 2박3일 + 도보
# day1: 해운대역 → 코오롱씨클라우드호텔
# day2: 코오롱씨클라우드호텔 → 코오롱씨클라우드호텔 (광안리 경유)
# day3: 코오롱씨클라우드호텔 → 부산역
# ══════════════════════════════════════════════════════════════════════
mock_endpoint_3day_walk: UserInput = {
    "route_type":       "endpoint",
    "travel_days":      3,
    "travel_date":      "2025-06-15",
    "transport":        "walk",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
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
        {
            "day_number":     3,
            "start_lat":      35.1602, "start_lng": 129.1607,
            "start_name":     "코오롱씨클라우드호텔",
            "start_address":  "부산 해운대구 우동 1408-5",
            "start_place_id": "11819137",
            "mid_lat":        35.1003, "mid_lng": 129.0305,
            "mid_name":       "남포동",
            "end_lat":        35.1150, "end_lng": 129.0390,
            "end_name":       "부산역",
            "end_address":    "부산 동구 중앙대로 206",
            "end_place_id":   "8325722",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 8: 출발/도착 + 2박3일 + 자동차
# (케이스 7과 동일 경로, transport만 car)
# ══════════════════════════════════════════════════════════════════════
mock_endpoint_3day_car: UserInput = {
    "route_type":       "endpoint",
    "travel_days":      3,
    "travel_date":      "2025-06-15",
    "transport":        "car",
    "companion":        "couple",
    "moods":            ["healing", "romantic"],
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
        {
            "day_number":     3,
            "start_lat":      35.1602, "start_lng": 129.1607,
            "start_name":     "코오롱씨클라우드호텔",
            "start_address":  "부산 해운대구 우동 1408-5",
            "start_place_id": "11819137",
            "mid_lat":        35.1003, "mid_lng": 129.0305,
            "mid_name":       "남포동",
            "end_lat":        35.1150, "end_lng": 129.0390,
            "end_name":       "부산역",
            "end_address":    "부산 동구 중앙대로 206",
            "end_place_id":   "8325722",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}


# ══════════════════════════════════════════════════════════════════════
# 케이스 9: 출발/도착 + 1박2일 + 자동차
# day1: 해운대역 → 코오롱씨클라우드호텔
# day2: 코오롱씨클라우드호텔 → 광안리해수욕장 (광안리 경유)
# ══════════════════════════════════════════════════════════════════════
mock_endpoint_2day_car: UserInput = {
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
            "end_lat":        35.1531, "end_lng": 129.1186,
            "end_name":       "광안리해수욕장",
            "end_address":    "부산 수영구 광안해변로 219",
            "end_place_id":   "7913310",
        },
    ],
    "start_time":       "11:00",
    "end_time":         "22:00",
    "companion_kr": None, "moods_kr": None, "activities_kr": None,
    "transport_kr": None, "duration_kr": None, "travel_weekday": None,
    "final_keywords": None, "name_search_keywords": None, "days_info": None,
}