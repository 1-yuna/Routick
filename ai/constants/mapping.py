# ─────────────────────────────────────────────────────────────────────
# mapping
# ─────────────────────────────────────────────────────────────────────
# Spring → AI Agent 변수값 매핑 테이블
# ─────────────────────────────────────────────────────────────────────

TRAVEL_DAYS_MAP = {
    1: "당일",
    2: "1박2일",
    3: "2박3일",
    4: "3박4일",
}

COMPANION_MAP = {
    "solo":     "혼자",
    "couple":   "연인",
    "friend":   "친구",
    "parents":  "부모님과",
    "children": "자녀와",
    "pet":      "반려동물과",
}

AGE_GROUP_MAP = {
    "10s":    "10대",
    "20s":    "20대",
    "30s":    "30대",
    "40s":    "40대",
    "50plus": "50대",
}

TRANSPORT_MAP = {
    "walk": "도보",
    "car":  "자동차",
}

MOODS_MAP = {
    "active":      "활기찬",
    "healing":     "힐링",
    "sensibility": "감성",
    "quiet":       "조용한",
    "warm":        "따뜻한",
    "romantic":    "로맨틱",
    "clean":       "깔끔한",
    "vintage":     "빈티지",
    "hip":         "힙한",
}

ACTIVITIES_MAP = {
    "tour/exhibition":      "관광/전시",
    "performance/culture":  "공연/문화",
    "thrill/experience":    "스릴/체험",
    "entertainment/sports": "오락/스포츠",
    "nature/walk":          "자연/산책",
    "shopping":             "쇼핑",
    "indoor":               "실내오락",
    "bar":                  "술/바",
}

# ─── 이동수단/여행기간 기반 검색 반경 (km) ───
RADIUS_MAP = {
    "walk": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    "car":  {1: 5.0, 2: 8.0, 3: 10.0, 4: 12.0},
}