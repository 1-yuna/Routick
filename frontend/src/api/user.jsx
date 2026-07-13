import api from './axios';

// 내 정보 조회 (스플래시 로그인 상태 확인 겸용)
export const getMe = () => api.get('/users/me');
