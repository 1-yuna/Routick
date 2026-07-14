const STATUS_LABEL = {
  OPEN: '영업 중',
  BREAK_TIME: '브레이크 타임',
  CLOSED: '휴무',
  UNKNOWN: '정보 없음',
};

// place 블록 하나 정규화: imageUrl -> src, 영문 status -> 한글
const normalizeBlock = (block) => {
  if (block.type !== 'place') return block;
  return {
    ...block,
    src: block.imageUrl ?? block.src ?? null,
    status: STATUS_LABEL[block.status] ?? block.status ?? '정보 없음',
  };
};

// 코스 생성 API 응답 -> 프론트 렌더링 형태로 정규화 (mock 데이터 넣어도 안전, 이미 한글/src면 그대로 통과)
export const normalizeCourse = (course) => {
  if (!course?.days) return course;
  return {
    ...course,
    days: course.days.map((day) => ({
      ...day,
      blocks: day.blocks.map(normalizeBlock),
    })),
  };
};
