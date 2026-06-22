import { create } from 'zustand';
import { mockCourse } from '../data/mock/courses.jsx';

const useCourseStore = create((set) => ({
  course: mockCourse,
  setCourse: (course) => set({ course }),
  reset: () => set({ course: mockCourse }),

  // 장소 추가
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
          {
            blockOrder: lastBlockOrder + 1,
            type: 'walk',
            mode: transport === 'car' ? 'car' : 'walk',
            minutes: moveMinutes,
          },
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

  // 블록 삭제
  // uids: _uid 형식 배열 (place-{placeId}-{dayNumber} 또는 parking-{name}-{dayNumber}-{blockOrder})
  // 삭제 후 첫 블록이 walk면 자동 제거, parking이면 유지
  deleteBlocks: (uids) =>
    set((state) => {
      const days = state.course.days.map((day) => {
        const toDeleteUids = uids.filter((uid) => {
          const parts = uid.split('-');
          const dayNum = uid.startsWith('place-')
            ? Number(parts[parts.length - 1])
            : Number(parts[parts.length - 2]);
          return dayNum === day.dayNumber;
        });

        if (toDeleteUids.length === 0) return day;

        // 대상 블록 제거
        let filtered = day.blocks.filter((b) => {
          if (b.type === 'place') {
            return !toDeleteUids.includes(
              `place-${b.placeId}-${day.dayNumber}`
            );
          }
          if (b.type === 'parking') {
            return !toDeleteUids.includes(
              `parking-${b.name}-${day.dayNumber}-${b.blockOrder}`
            );
          }
          return true;
        });

        // 맨 앞 walk 제거
        while (filtered.length > 0 && filtered[0].type === 'walk') {
          filtered = filtered.slice(1);
        }

        // 맨 뒤 walk 제거
        while (
          filtered.length > 0 &&
          filtered[filtered.length - 1].type === 'walk'
        ) {
          filtered = filtered.slice(0, -1);
        }

        // 연속 walk → 하나만
        const deduped = [];
        for (const block of filtered) {
          if (
            block.type === 'walk' &&
            deduped[deduped.length - 1]?.type === 'walk'
          ) {
            continue;
          }
          // parking 다음 walk → parking의 exitTransport가 이미 이동시간 표시하므로 walk 제거
          if (
            block.type === 'walk' &&
            deduped[deduped.length - 1]?.type === 'parking'
          ) {
            continue;
          }
          deduped.push(block);
        }

        // parking 연속 시 exitTransport 병합
        const merged = [];
        for (const block of deduped) {
          const prev = merged[merged.length - 1];
          if (block.type === 'parking' && prev?.type === 'parking') {
            merged[merged.length - 1] = { ...prev, exitTransport: undefined };
            merged.push({
              ...block,
              enterTransport: prev.exitTransport ?? block.enterTransport,
            });
          } else {
            merged.push(block);
          }
        }

        // blockOrder 재정렬
        const reordered = merged.map((block, idx) => ({
          ...block,
          blockOrder: idx + 1,
        }));

        return { ...day, blocks: reordered };
      });

      return { course: { ...state.course, days } };
    }),

  // 블록 순서 변경 (blockOrder 재정렬)
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

  // 특정 day의 blocks 직접 교체 (재계산 결과 반영용)
  updateBlocks: (dayNumber, newBlocks) =>
    set((state) => {
      const days = state.course.days.map((day) => {
        if (day.dayNumber !== dayNumber) return day;
        return { ...day, blocks: newBlocks };
      });
      return { course: { ...state.course, days } };
    }),
}));

export default useCourseStore;
