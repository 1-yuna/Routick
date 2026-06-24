import { create } from 'zustand';
import { mockUser } from '../data/mock/user.jsx';

// 내 정보 전역 상태 관리
const useUserStore = create((set) => ({
  user: mockUser,
  updateUser: (data) => set((state) => ({ user: { ...state.user, ...data } })),
}));

export default useUserStore;
