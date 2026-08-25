# ─────────────────────────────────────────────────────────────────────
# select_itinerary_prompt
# ─────────────────────────────────────────────────────────────────────
# 최적 일정 선택에서 사용되는 LLM 프롬프트
#
# day별 검증 통과 동선 후보를 한 번에 모두 보여주고 day별로 1개씩 선택시킴
# (day 간 동일 장소 중복을 피하려면 day를 따로따로 판단하면 안 되고
#  전체를 한 번에 봐야 하므로 day 병렬 호출이 아니라 단일 호출)
# ─────────────────────────────────────────────────────────────────────


# ─── 동선 1개를 LLM 프롬프트용 텍스트로 축약 ───
def _format_route(route: dict, idx: int) -> str:
    lines = [f"  [동선 {idx}] (적합도 총점 {route['total_score']}점)"]
    for p in route["places"]:
        atmosphere = ", ".join(p.get("atmosphere", [])) or "정보없음"
        matched    = ", ".join(p.get("matched_activities", [])) or "없음"
        anchor_mark = " 🎯앵커" if p.get("query_name") else ""
        lines.append(
            f"    - {p.get('name')} (id: {p.get('id')}, 유형: {p.get('bucket')}, "
            f"{p.get('total_score')}점){anchor_mark} | 분위기: {atmosphere} | "
            f"매칭활동: {matched} | {p.get('summary', '')}"
        )
    return "\n".join(lines)


# ─── 프롬프트 ───
def build_prompt(valid_routes_by_day: dict[int, list[dict]], user_input: dict) -> str:
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

    for day_number in sorted(valid_routes_by_day.keys()):
        routes = valid_routes_by_day[day_number]
        if len(routes) == 1:
            single_candidate_days.append(day_number)

        route_lines = [_format_route(r, idx) for idx, r in enumerate(routes)]
        day_blocks.append(f"[day{day_number}] (후보 {len(routes)}개)\n" + "\n".join(route_lines))

    days_text = "\n\n".join(day_blocks)

    single_note = ""
    if single_candidate_days:
        days_str = ", ".join(f"day{d}" for d in single_candidate_days)
        single_note = f"""
    ※ {days_str}는 후보가 1개뿐입니다. 이 day는 selected_route_index=0으로 고정하고,
      select_reason은 "후보가 1개뿐이라 자동 선택됨"으로 작성하세요.
    """

    return f"""
    아래는 day별 동선 후보입니다. day별로 후보 중 가장 적합한 동선 1개를 선택하고,
    JSON으로만 응답하세요. 설명, 마크다운, 코드블록 금지.

    {user_context}

    [선택 기준]
    1. 사용자의 분위기·활동 선호와 가장 잘 맞는 동선을 우선하세요.
    2. 각 장소의 적합도 점수(총점)가 높은 장소들로 구성된 동선을 우선하세요.
    3. 음식점·카페·활동 장소의 구성이 자연스럽고 다양한지 판단하세요
       (같은 분위기·활동 태그만 반복되는 동선은 감점 요인입니다).
    4. 여러 day의 최종 선택 동선에 동일 장소(id)가 중복되지 않아야 합니다.
       가장 중요한 기준이니, 특정 day만 보고 고르지 말고 전체 day 조합 관점에서
       중복이 없는 조합이 되도록 선택하세요.
    {single_note}

    [day별 선택 이유 작성 기준]
    - select_reason: 왜 이 동선을 선택했는지 핵심 이유를 1~2문장으로 작성하세요.
    - place_reasons: 선택한 동선에 포함된 "모든" 장소 각각에 대해, 왜 이 장소가 이
      동선에 어울리는지(분위기·활동 매칭, 동선 내 구성상 역할, 앵커 여부 등) 1문장으로
      작성하세요. place_id는 후보 목록에 적힌 id를 그대로 쓰세요. 누락 없이 동선의
      장소 수만큼 채우세요.

    [응답 형식]
    {{
      "days": [
        {{
          "day_number": 1,
          "selected_route_index": 0,
          "select_reason": "선택 이유",
          "place_reasons": [
            {{"place_id": "장소id", "reason": "이 장소를 고른 이유"}}
          ]
        }}
      ]
    }}

    [동선 후보]
    {days_text}
    """