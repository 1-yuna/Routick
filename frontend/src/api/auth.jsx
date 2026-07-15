import api from './axios';

// 서버 에러 응답에서 메시지 추출
export const getErrorMessage = (
  error,
  fallback = '잠시 후 다시 시도해주세요'
) => error.response?.data?.message ?? fallback;

// 이메일 인증번호 발송
export const sendEmailCode = (email) => api.post('/auth/email/send', { email });

// 이메일 인증번호 확인
export const verifyEmailCode = (email, code) =>
  api.post('/auth/email/verify', { email, code });

// 회원가입
export const signup = (nickname, email, password) =>
  api.post('/auth/signup', { nickname, email, password });

// 로그인 (토큰은 httpOnly 쿠키로 자동 설정됨)
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

// 로그아웃
export const logout = () => api.post('/auth/logout');
