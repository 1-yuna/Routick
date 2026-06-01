import { create } from 'zustand';

// 8단계 코스 선택 데이터 전역 상태 관리
const useSelectionStore = create((set) => ({
  // 선택 데이터 초기값
  address: { name: '', lat: '', lng: '', placeId: '' },
  period: '',
  companion: '',
  age: '',
  mood: [],
  activity: [],
  transport: '',
  dislike: [],

  setAddress: (data) => set({ address: data }),
  setPeriod: (data) => set({ period: data }),
  setCompanion: (data) => set({ companion: data }),
  setAge: (data) => set({ age: data }),
  // 다중 선택 - 이미 선택된 값이면 제거, 없으면 추가
  setMood: (value) =>
    set((state) => ({
      mood: state.mood.includes(value)
        ? state.mood.filter((v) => v !== value)
        : [...state.mood, value],
    })),
  // 다중 선택 - 이미 선택된 값이면 제거, 없으면 추가
  setActivity: (value) =>
    set((state) => ({
      activity: state.activity.includes(value)
        ? state.activity.filter((v) => v !== value)
        : [...state.activity, value],
    })),
  setTransport: (data) => set({ transport: data }),
  setDislike: (data) => set({ dislike: data }),

  // 홈으로 돌아갈 때 전체 초기화
  reset: () =>
    set({
      address: { name: '', lat: '', lng: '', placeId: '' },
      period: '',
      companion: '',
      age: '',
      mood: [],
      activity: [],
      transport: '',
      dislike: [],
    }),
}));

export default useSelectionStore;
