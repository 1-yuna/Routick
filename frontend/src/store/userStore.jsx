import { create } from 'zustand';

// 내 정보 전역 상태 관리 (로그인 응답/GET /users/me 데이터가 그대로 들어감)
const useUserStore = create((set) => ({
  user: null, // { userId, nickname, email, profileImageUrl, provider, lastLocation, createdAt }
  setUser: (user) => set({ user }),
  updateUser: (data) => set((state) => ({ user: { ...state.user, ...data } })),
  clearUser: () => set({ user: null }),
}));

export default useUserStore;
