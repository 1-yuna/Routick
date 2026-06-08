# ─────────────────────────────────────────────────────────────────────
# select_itinerary_prompt
# ─────────────────────────────────────────────────────────────────────
# select_itinerary 노드에서 사용되는 프롬프트
# ─────────────────────────────────────────────────────────────────────

import json


def build_prompt(user_input: dict, summarized: list[dict]) -> str:
    companion_kr     = user_input.get("companion_kr", "")
    age_group        = user_input.get("age_group", "")
    moods_kr         = user_input.get("moods_kr", [])
    activities_kr    = user_input.get("activities_kr", [])
    transport_kr     = user_input.get("transport_kr", "도보")
    avoid_activities = user_input.get("avoid_activities", [])
    travel_days      = user_input.get("travel_days", 1)

    itineraries_text = json.dumps(summarized, ensure_ascii=False, indent=2)

    return f"""
아래는 여행 동선 후보 목록입니다.
유저 정보를 참고하여 {travel_days}일치 동선을 선택해주세요.
각 day마다 서로 다른 동선을 선택하고, 모든 day를 통틀어 동일한 장소(place_id)가 절대 중복되지 않도록 해주세요.
JSON 형식으로만 응답하세요. 설명, 마크다운, 코드블록 금지.

[유저 정보]
- 동행 유형: {companion_kr}
- 연령대: {age_group}
- 선호 분위기: {", ".join(moods_kr)}
- 선호 활동: {", ".join(activities_kr)}
- 이동 수단: {transport_kr}
- 피하고 싶은 것: {", ".join(avoid_activities) if avoid_activities else "없음"}
- 여행 기간: {travel_days}일

[판단 기준]
- companion + moods + activities 조합을 종합적으로 고려
- 장소의 name과 summary를 직접 참고하여 유저 분위기에 맞는지 스스로 판단하세요. atmosphere 필드가 잘못 분류됐을 수 있습니다.
- 유저가 선호하는 분위기(moods)와 잘 어울리는 장소가 많은 동선 우선
- 동선 내 장소들의 분위기 흐름이 자연스러운 동선 우선 (예: 활기찬 → 힐링 → 감성)
- 장소 다양성 (같은 유형 장소가 연속되지 않는 동선)
- 동선의 자연스러움 (흐름이 어색하지 않은 동선)
- 유저가 피하고 싶은 활동이 포함되지 않은 동선
- 모든 day를 통틀어 동일한 place_id가 절대 중복되어서는 안됨

[중요]
- recommendation_reasons는 모든 장소에 반드시 작성하세요. 빈 문자열 절대 금지.
- 모든 장소의 추천 이유는 필수입니다. 빈 문자열 절대 금지.
- 각 추천 이유는 장소 특성과 유저 취향을 반영하여 30자 이내로 작성하세요.
- 추천 이유는 "~합니다" 형태가 아닌 명사형으로 작성하세요. (예: "연인과 함께하기 좋은 오션뷰 카페", "힐링 분위기의 해안 산책로")
- 모든 day를 통틀어 동일한 place_id가 단 하나도 중복되어서는 안됩니다.
- 동선 내에서 이름이 유사하거나 같은 브랜드/체인인 장소가 중복되지 않도록 해주세요. (예: 블루라인파크 관련 장소가 같은 동선에 2개 이상 포함되면 안됨)

[동선 후보]
{itineraries_text}

[응답 형식]
{{
  "days": [
    {{
      "day_number": 1,
      "selected_index": 선택한 동선의 index (숫자),
      "reason": "이 동선을 선택한 이유 (1문장)",
      "recommendation_reasons": [
        {{
          "place_id": "장소id",
          "reason": "이 장소를 추천하는 이유 (1문장, 30자 이내)"
        }}
      ]
    }}
  ]
}}
"""