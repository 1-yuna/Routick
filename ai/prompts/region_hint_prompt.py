# ─────────────────────────────────────────────────────────────────────
# region_hint_prompt
# ─────────────────────────────────────────────────────────────────────
# region_hint 노드용 LLM 프롬프트
#
# 홈 지역추천 프롬프트와 동일한 규칙 재사용:
#   - 카테고리성 표현("OO동 카페거리") 대신 구체적 상호명·고유명사·거리명만 추출
#   - 뚜렷한 핫플이 없는 지역도 있으므로 "최소 0개 ~ 최대 5개" 허용
#     (정확히 N개를 강요하면 지역에 안 맞는 장소를 억지로 만들어낼 수 있음)
#
# *(v3.1)* travel_mode(도보/자동차) + route_type 반영:
#   - 자동차 + only(목적지만 선택): 차로 20~30분 내 범위까지 허용하되,
#     지역에서 가까운 곳을 항상 우선하도록 명시
#     (가깝고 유명한 곳을 두고 먼 곳부터 나오는 것 방지)
#   - 그 외 전부 (도보, 또는 endpoint 케이스): 근처에 몰려 있는 장소만
#     endpoint는 day별 mid가 그 날의 중심이므로 이동수단과 무관하게
#     mid 근처를 벗어나면 안 됨 (다른 day 지역과 힌트가 섞이는 것 방지)
#   → 힌트가 collect_pool의 수집 앵커(중심점)로 쓰이므로,
#     조건에 맞지 않는 거리의 앵커가 나오는 것을 입구에서 차단
# ─────────────────────────────────────────────────────────────────────


def build_prompt(
    region_name:   str,
    moods_kr:      list[str],
    activities_kr: list[str],
    transport:     str = "walk",   # walk / car
    route_type:    str = "only",   # only / endpoint
) -> str:
    mood_text     = ", ".join(moods_kr) if moods_kr else "특별한 선호 없음"
    activity_text = ", ".join(activities_kr) if activities_kr else "특별한 선호 없음"

    transport_text = "자동차 여행" if transport == "car" else "도보 여행"

    if transport == "car" and route_type == "only":
        distance_rule = (
            f'3. "{region_name}"에서 가까운 곳을 최우선으로 할 것.\n'
            f'   가까운 유명 장소가 5개 미만일 때만 차로 20~30분 내 장소로 나머지를 채울 것'
        )
    else:
        distance_rule = (
            f'3. 반드시 "{region_name}" 바로 근처, 서로 가깝게 몰려 있는 곳만 답할 것.\n'
            f'   다른 동네의 유명 장소는 아무리 유명해도 포함하지 말 것'
        )

    return f"""당신은 국내 여행 전문가입니다. "{region_name}" 근처에서 실제로 여행자들이 많이 찾는
구체적인 장소나 거리 이름을 알려주세요.

여행자 선호:
- 이동수단: {transport_text}
- 분위기: {mood_text}
- 활동: {activity_text}

규칙:
1. "OO동 카페거리", "번화가", "먹자골목" 같은 카테고리성/추상적 표현은 절대 쓰지 말 것
2. 실제 존재하는 구체적인 상호명·거리명·명소명만 추출
   (예: "논골담길", "도째비골 스카이밸리" — 이런 식의 고유명사)
{distance_rule}
4. 뚜렷하게 유명한 곳이 없으면 억지로 만들지 말고 빈 배열을 반환할 것
5. 최소 0개 ~ 최대 5개

아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "places": ["장소명1", "장소명2", ...]
}}
"""