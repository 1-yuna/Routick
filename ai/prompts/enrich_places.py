# ─────────────────────────────────────────────────────────────────────
# enrich_places
# ─────────────────────────────────────────────────────────────────────
# 2차 필터에서 사용되는 프롬프트
# 장소 데이터를 LLM으로 보강하기 위한 프롬프트
# ─────────────────────────────────────────────────────────────────────


# ─── 프롬프트 ───
def build_prompt(
        blog_data: list[dict],
        user_input: dict,
) -> str:
    companion_kr = user_input.get("companion_kr", "")
    age_group = user_input.get("age_group", "")

    user_context = f"""
    [현재 사용자 정보]
    - 동행 유형: {companion_kr}
    - 연령대: {age_group}

    이 정보는 장소 분위기와 추천 대상을 해석할 때 참고하세요.
    단, 실제 블로그 리뷰 기반으로 장소 자체 특성을 우선 판단하세요.
    """

    lines = []
    for i, item in enumerate(blog_data, 1):
        snippets = "\n".join(f"  - {s}" for s in item["snippets"]) or "  - 블로그 없음"
        category = item.get("category", "")
        lines.append(f"""[{i}] {item['name']} (id: {item['place_id']})
  카테고리: {category}
{snippets}""")

    places_text = "\n\n".join(lines)

    return f"""
    아래는 여행지 장소들의 블로그 리뷰 발췌입니다.
    각 장소에 대해 JSON 배열로만 응답하세요.
    설명, 마크다운, 코드블록 금지.

    {user_context}

    - 블로그 리뷰 기반으로 추론하세요. 정보 부족해도 반드시 추론해서 채우세요.
    - 모든 필드 필수. 빈 배열/빈 문자열 금지.
    - summary: 장소 이름과 블로그 내용 참고, 30자 이내 명사형. "~입니다" 금지.
    - atmosphere: 활기찬/힐링/감성/이색/조용한/따뜻한/로맨틱/깔끔한/빈티지/힙한 중 최대 3개.
    - best_for: 연인/혼자/친구/부모님과/자녀와/반려동물과 중 최대 3개.
    - bucket: cafe/food/activity/lodging/other 중 1개.
    - place_tags: 아래 [목록]에 있는 값만 사용. 목록 외 값("기타", "food", "cafe", "activity" 등) 절대 금지.
      bucket이 cafe 또는 lodging → 빈 배열.
      나머지(food/activity/other) → 반드시 목록에서 1개 선택.
      목록에 정확히 없으면 가장 유사한 것을 반드시 선택.
      (예: 만화카페/방탈출/보드게임 → 이색카페 / 하천/강/공원 → 산책로 / 볼링/당구/노래방 → 오락 / 클라이밍/배드민턴 → 스포츠 / 와인바/칵테일바/이자카야 → 바/술집 / 삼겹살/갈비/대창 → 고기 / 궁/사찰/유적지/역사 탐방 → 역사/문화)

      [목록]
      이색카페, 오락, 스포츠, 역사/문화,
      산책로, 해변/바다, 등산/산,
      전시관/미술관, 서점, 이색체험, 놀이공원, 아쿠아리움, 영화관, 쇼핑,
      한식, 일식, 양식, 중식, 분식, 고기, 바/술집

    [atmosphere 판단 기준]
    활기찬: 웨이팅이 있거나 회전율이 빠른 곳 / 시장, 번화가, 인기 맛집, 관광지
    힐링: 조용하고 편안하게 쉬기 좋은 공간 / 자연 요소(바다, 숲, 공원)가 있는 장소
    감성: 인스타 감성, 조명, 인테리어, 사진찍기 좋은 공간 / 공간 자체의 "예쁨"이 중요한 곳
    이색: 체험형 공간, 테마형 공간, 독특한 구조 / 기존에 흔하지 않은 경험을 제공하는 장소
    조용한: 대화하거나 혼자 머물기 좋은 낮은 소음 환경 / 회전율이 낮고 여유로운 분위기
    따뜻한: 아늑하고 편안한 느낌의 공간 / 소규모 운영 또는 개인적인 감성이 있는 장소
    로맨틱: 데이트 목적에 자연스럽게 어울리는 공간 / 야경, 오션뷰, 분위기 좋은 조명
    깔끔한: 구조가 단순하고 현대적인 느낌 / 정돈된 인테리어와 신축 공간에서 자주 나타남
    빈티지: 오래된 인테리어, 레트로 감성 / 옛날 건물, 오래된 가구, 클래식한 분위기
    힙한: 트렌디하고 젊은 감각의 공간 / SNS에서 유행하거나 핫플인 장소 / 감각적인 디자인

    [best_for 판단 기준]
    연인: 야경, 분위기 좋은 카페, 오션뷰, 사진찍기 좋은 곳, 데이트하기 좋은 곳
    혼자: 혼밥, 혼카페, 조용히 머물기 좋은 장소
    친구: 함께 놀거나 대화하기 좋은 장소 / 활동적이거나 시끌벅적한 장소
    부모님과: 자연, 온천, 문화시설, 사찰 등 / 조용하고 여유로운 장소
    자녀와: 아이 동반 가능 장소 / 동물원, 아쿠아리움, 놀이공원, 체험 공간
    반려동물과: 야외, 공원, 펫 프렌들리 카페, 산책로

    [응답 형식]
    [
      {{
        "place_id": "장소id",
        "bucket": "cafe"|"food"|"activity"|"lodging"|"other",
        "atmosphere": [],
        "best_for": [],
        "place_tags": [],
        "revisit_intent": "high"|"medium"|"low",
        "summary": "30자 이내 한 문장"
      }}
    ]

    [응답 예시]
    [
      {{"place_id": "111", "bucket": "activity", "atmosphere": ["이색", "활기찬"], "best_for": ["연인", "친구"], "place_tags": ["이색카페"], "revisit_intent": "high", "summary": "홍대 대표 만화카페"}},
      {{"place_id": "222", "bucket": "food", "atmosphere": ["활기찬"], "best_for": ["친구"], "place_tags": ["고기"], "revisit_intent": "medium", "summary": "인기 있는 삼겹살 맛집"}},
      {{"place_id": "333", "bucket": "cafe", "atmosphere": ["감성", "로맨틱"], "best_for": ["연인"], "place_tags": [], "revisit_intent": "high", "summary": "오션뷰가 멋진 감성 카페"}},
      {{"place_id": "444", "bucket": "activity", "atmosphere": ["힐링"], "best_for": ["연인"], "place_tags": ["산책로"], "revisit_intent": "medium", "summary": "홍제천 힐링 산책 코스"}},
      {{"place_id": "555", "bucket": "food", "atmosphere": ["로맨틱"], "best_for": ["연인"], "place_tags": ["바/술집"], "revisit_intent": "high", "summary": "분위기 있는 칵테일바"}}
    ]

    {places_text}
    """