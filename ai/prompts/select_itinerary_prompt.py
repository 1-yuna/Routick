# ─────────────────────────────────────────────────────────────────────
# select_itinerary_prompt
# ─────────────────────────────────────────────────────────────────────
# 3-7 최적 일정 선택에서 사용되는 LLM 프롬프트
#
# 핵심 역할:
#   1. day별 동선 후보를 전체적으로 한 번에 검토하여 day별 최적 동선 1개씩 선택
#      - companion + moods + activities 종합 판단
#      - best_for에 companion 포함 비중이 높은 동선 우선
#      - 무드 전개(atmosphere 순서) 자연스러움 평가
#      - place_tags 기반 활동 다양성 판단
#      - day 간 동일 장소 중복 금지를 최우선으로 고려
#      - 동선 내 동일 place_tags 2개 이상 금지
#   2. 각 장소별 추천 이유 생성 (moods/activities 매칭 포함, 30자 이내)
#   3. day별 선택 이유 + 비교(미선택) 이유 생성
# ─────────────────────────────────────────────────────────────────────


# ─── 동선 1개를 LLM 프롬프트용 텍스트로 축약 ───
def _format_itinerary(itinerary: list[dict]) -> str:
    # start/end/parking 블록 제외, 일반 장소만 포함
    places = [
        item for item in itinerary
        if item["place"].get("bucket") not in ("start", "end", "parking")
    ]

    lines = []
    for item in places:
        p = item["place"]
        atmosphere = ", ".join(p.get("atmosphere", [])) or "정보없음"
        best_for   = ", ".join(p.get("best_for", [])) or "정보없음"
        tags       = ", ".join(p.get("place_tags", [])) or "정보없음"
        summary    = p.get("summary", "")
        lines.append(
            f"    - {p.get('name')} (id: {p.get('id')}) "
            f"| 분위기: {atmosphere} | 추천대상: {best_for} | 활동: {tags} | {summary}"
        )
    return "\n".join(lines)


# ─── 프롬프트 ───
def build_prompt(
        itineraries_by_day: dict[int, list[list[dict]]],
        user_input: dict,
) -> str:
    companion_kr  = user_input.get("companion_kr", "")
    moods_kr      = user_input.get("moods_kr") or []
    activities_kr = user_input.get("activities_kr") or []

    user_context = f"""
    [현재 사용자 정보]
    - 동행 유형: {companion_kr}
    - 선호 분위기: {", ".join(moods_kr) if moods_kr else "없음"}
    - 선호 활동: {", ".join(activities_kr) if activities_kr else "없음"}
    """

    day_blocks = []
    single_candidate_days = []

    for day_number in sorted(itineraries_by_day.keys()):
        itineraries = itineraries_by_day[day_number]

        if len(itineraries) == 1:
            single_candidate_days.append(day_number)

        candidate_lines = []
        for idx, itinerary in enumerate(itineraries):
            candidate_lines.append(
                f"  [동선 {idx}]\n{_format_itinerary(itinerary)}"
            )
        day_blocks.append(
            f"[day{day_number}] (후보 {len(itineraries)}개)\n" + "\n".join(candidate_lines)
        )

    days_text = "\n\n".join(day_blocks)

    single_note = ""
    if single_candidate_days:
        days_str = ", ".join(f"day{d}" for d in single_candidate_days)
        single_note = f"""
    ※ {days_str}는 후보가 1개뿐입니다. 이 day는 selected_index=0으로 고정하고,
      select_reason과 compare_reason은 "후보가 1개뿐이라 자동 선택됨"으로 작성하세요.
      (단, recommendation_reasons는 동일하게 생성하세요.)
    """

    return f"""
    아래는 여행 일정 동선 후보입니다. day별로 후보 동선 중 가장 적합한 1개를 선택하고,
    JSON으로만 응답하세요. 설명, 마크다운, 코드블록 금지.

    {user_context}

    [선택 기준]
    1. companion + moods + activities 조합을 종합적으로 고려해 day별 최적 동선을 선택하세요.
    2. best_for에 동행 유형({companion_kr})이 포함된 장소 비중이 높은 동선을 우선하세요.
    3. 무드 전개를 평가하세요: 동선 순서(시간 흐름)대로 atmosphere가 자연스럽게 이어지는지 확인합니다.
       예) 활기찬 → 힐링 → 감성처럼 점진적으로 전환되는 흐름은 긍정적으로 평가하세요.
           활기찬 → 조용한 → 활기찬처럼 극단적으로 반복 전환되는 흐름은 감점 요인입니다.
    4. place_tags 기반으로 활동의 다양성을 판단하세요. 동선 내 동일 place_tags가
       2개 이상이면 감점 요인입니다.
    5. day 간 동일 장소(id) 중복을 최우선으로 피하세요. 여러 day에서 좋은 동선이
       같은 장소를 포함하고 있다면, 전체 조합 관점에서 중복이 없는 조합을 선택하세요.
    {single_note}

    [장소별 추천 이유 작성 기준]
    - 동선 내 모든 일반 장소(food/cafe/activity/browse/pop)에 대해 빠짐없이 작성하세요.
      장소를 하나라도 빠뜨리면 안 됩니다.
    - 유저가 선택한 분위기(moods) 또는 활동(activities) 중 매칭되는 항목을 반드시 포함하세요.
    - 30자 이내, 명사형으로 작성하세요. "~입니다", "~해요" 등 종결어미 금지.
    - 형식 예시: "로맨틱한 분위기의 오션뷰 카페", "활기찬 분위기의 현지 인기 맛집"

    [day별 선택/비교 이유 작성 기준]
    - select_reason: 왜 이 동선을 선택했는지 핵심 이유를 1~2문장으로 작성하세요.
    - compare_reason: 다른 후보 동선들과 비교했을 때 어떤 점에서 더 나았는지 1문장으로 작성하세요.

    [응답 형식]
    {{
      "days": [
        {{
          "day_number": 1,
          "selected_index": 0,
          "select_reason": "선택 이유",
          "compare_reason": "다른 후보 대비 선택 이유 요약",
          "recommendation_reasons": [
            {{"place_id": "장소id", "reason": "30자 이내 추천 이유"}}
          ]
        }}
      ]
    }}

    [동선 후보]
    {days_text}
    """