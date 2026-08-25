# ─────────────────────────────────────────────────────────────────────
# region_hint_prompt
# ─────────────────────────────────────────────────────────────────────
# 여행 권역 조회 노드용 LLM 프롬프트
# ─────────────────────────────────────────────────────────────────────


def build_prompt(
    context_name: str,
    moods_kr: list[str],
    activities_kr: list[str],
    avoid_anchors: list[str],
) -> str:
    mood_text     = ", ".join(moods_kr) if moods_kr else "특별한 선호 없음"
    activity_text = ", ".join(activities_kr) if activities_kr else "특별한 선호 없음"
    avoid_text    = ", ".join(avoid_anchors) if avoid_anchors else "없음"

    return f"""당신은 국내 여행 전문가입니다. "{context_name}" 근처에서 하루 코스로 다닐 만한
여행 앵커 장소를 제안해주세요.

여행자 조건:
- 분위기: {mood_text}
- 활동: {activity_text}

이미 다른 날짜에 사용한 앵커 장소(중복 금지): {avoid_text}

규칙:
1. concept과 reason은 여행자 조건과 연결해서 1~2문장으로 작성할 것
2. anchors는 "{context_name}" 근처의 인기있는 맛집/카페/놀거리 중 정확히 2~3개
   - 서로 겹치지 않는 성격(맛집/카페/놀거리)으로 다양하게 구성할 것
   - 최소 1개는 이 지역 하면 바로 떠오르는, 검색하면 바로 나올 정도로 유명한 곳으로 넣을 것
   - 이름에 괄호나 부가 설명을 붙이지 말 것 (예: "경의선숲길(연남동 구간)" 금지 → "경의선숲길공원")
     지도 앱에서 검색 가능한 정확한 상호명·가게명만 그대로 쓸 것. 행정지명 안되고 특정 가게만 가능 (예: "홍대걷고싶은거리" 금지)
   
3. 이미 사용한 앵커 장소, 이름이 겹치는 장소, 좌표가 같은 장소는 절대 다시 제안하지 말 것

아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "concept": "...",
  "reason": "...",
  "anchors": ["장소명1", "장소명2", "장소명3"]
}}
"""