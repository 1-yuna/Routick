import { create } from 'zustand';

// 9단계 코스 선택 데이터 전역 상태 관리
const useSelectionStore = create((set) => ({
  // 1단계: 여행 기간 (CS-02)
  period: '',
  // 2단계: 여행 날짜 (CS-03)
  date: '',
  // 3단계: 이동 수단 (CS-04)
  transport: '',
  // 4단계: 동선 여부 (CS-05) - 'destination' | 'route'
  route: '',
  // 5단계: 여행 장소 (CS-06)
  address: { name: '', lat: '', lng: '', placeId: '' },
  addresses: [], // [{ start: {...}, end: {...} }, ...]
  // 6단계: 동행자 (CS-07)
  companion: '',
  // 7단계: 분위기 선호 (CS-08) - 다중 선택
  mood: [],
  // 8단계: 활동 선호 (CS-09) - 다중 선택
  activity: [],
  // 9단계: 비선호 키워드 (CS-10) - 자유 입력, 다중 추가
  dislike: [],

  setPeriod: (data) => set({ period: data }),
  setDate: (data) => set({ date: data }),
  setTransport: (data) => set({ transport: data }),
  setRoute: (data) => set({ route: data }),
  setAddress: (data) => set({ address: data }),
  setAddresses: (data) => set({ addresses: data }),
  setCompanion: (data) => set({ companion: data }),
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
  // 비선호 키워드 추가
  addDislike: (keyword) =>
    set((state) => ({
      dislike: state.dislike.includes(keyword)
        ? state.dislike
        : [...state.dislike, keyword],
    })),
  // 비선호 키워드 제거
  removeDislike: (keyword) =>
    set((state) => ({
      dislike: state.dislike.filter((v) => v !== keyword),
    })),

  // 홈으로 돌아갈 때 전체 초기화
  reset: () =>
    set({
      period: '',
      date: '',
      transport: '',
      route: '',
      address: { name: '', lat: '', lng: '', placeId: '' },
      addresses: [],
      companion: '',
      mood: [],
      activity: [],
      dislike: [],
    }),
}));

export default useSelectionStore;
