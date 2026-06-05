import { create } from 'zustand';

// 내 정보 전역 상태 관리
const useUserStore = create((set) => ({
  user: {
    name: '김윤아',
    accountType: '이메일',
    src: null,
  },
  updateUser: (data) => set((state) => ({ user: { ...state.user, ...data } })),
}));

export default useUserStore;
