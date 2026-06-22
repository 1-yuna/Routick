import { create } from 'zustand';
import { mockCourse } from '../data/mock/courses.jsx';

const useCourseStore = create((set) => ({
  course: mockCourse,
  setCourse: (course) => set({ course }),
  reset: () => set({ course: mockCourse }),

  // 장소 추가
  // transport: 'car' | 'walk' → 이동 블록 mode 결정
  addPlace: (place, dayNumber = 1, moveMinutes = 10, transport = 'walk') =>
    set((state) => {
      const days = state.course.days.map((day) => {
        if (day.dayNumber !== dayNumber) return day;

        const blocks = day.blocks;
        const lastBlockOrder = blocks[blocks.length - 1]?.blockOrder ?? 0;
        const lastPlaceOrder = blocks
          .filter((b) => b.type === 'place')
          .reduce((max, b) => Math.max(max, b.placeOrder ?? 0), 0);

        const newBlocks = [
          ...blocks,
          // 이동 블록 - transport에 따라 mode 결정
          {
            blockOrder: lastBlockOrder + 1,
            type: 'walk', // walk 타입 유지, mode로 도보/자동차 구분
            mode: transport === 'car' ? 'car' : 'walk',
            minutes: moveMinutes,
          },
          // 장소 블록
          {
            blockOrder: lastBlockOrder + 2,
            type: 'place',
            placeOrder: lastPlaceOrder + 1,
            placeId: place.placeId,
            name: place.name,
            bucket: place.bucket ?? 'other',
            src: place.src ?? null,
            status: place.status ?? '정보 없음',
            description: place.description ?? '',
            lat: place.lat,
            lng: place.lng,
            stayMinutes: place.stayMinutes,
            arriveTime: place.arriveTime,
            leaveTime: place.leaveTime,
          },
        ];

        return { ...day, blocks: newBlocks };
      });

      return { course: { ...state.course, days } };
    }),

  // 블록 순서 변경
  reorderBlocks: (dayNumber, newBlocks) =>
    set((state) => {
      const days = state.course.days.map((day) => {
        if (day.dayNumber !== dayNumber) return day;
        const reordered = newBlocks.map((block, idx) => ({
          ...block,
          blockOrder: idx + 1,
        }));
        return { ...day, blocks: reordered };
      });
      return { course: { ...state.course, days } };
    }),
}));

export default useCourseStore;
