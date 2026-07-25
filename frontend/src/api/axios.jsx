import axios from 'axios';

// 공용 axios 인스턴스
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // http://localhost:8080/api/v1
  withCredentials: true, // httpOnly 쿠키 전송 필수
});

// *(fix)* refresh/로그인 관련 요청은 재발급 트리거에서 제외
// - /auth/refresh 자체가 401을 받으면(리프레시 토큰도 만료) 여기서 또 재발급을
//   시도하면 무한 재귀/중복 호출 위험이 있음 → 즉시 로그인 화면으로 보내야 함
// - /auth/login, /auth/signup은 "비밀번호 틀림" 같은 정상적인 401인데
//   여기 걸리면 의미 없는 재발급 시도 후 로그인 페이지로 튕기는 이상한 흐름이 됨
const AUTH_EXEMPT_PATHS = [
  '/auth/login',
  '/auth/signup',
  '/auth/refresh',
  '/auth/email/send',
  '/auth/email/verify',
];

// 401 처리: accessToken 만료 시 재발급 후 원 요청 1회 재시도
let refreshPromise = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;

    // *(fix)* 이전엔 `code === 'TOKEN_EXPIRED'`까지 정확히 일치해야만
    // 재발급을 시도했음 — 백엔드가 내려주는 에러 code 값이 이 문자열과
    // 조금이라도 다르면(대소문자, 필드명, 아예 code 필드가 없는 경우 등)
    // 이 조건이 항상 false가 되어 재발급 로직 자체가 실행되지 않고,
    // 그냥 401 에러가 호출부로 넘어가서 (로그아웃도, 재시도도 없이)
    // 화면이 조용히 기본값/빈 상태로 렌더링되는 지금 증상과 정확히 일치함.
    // → exempt 경로가 아닌 모든 401을 "토큰 만료로 간주하고 재발급 시도"로
    //   완화. 재발급 자체가 실패하면(리프레시 토큰도 만료 등) 기존처럼
    //   로그인 화면으로 보냄 — 백엔드가 실제로 못 보낸 code 값에 의존하지 않음.
    const isAuthExempt = AUTH_EXEMPT_PATHS.some((p) =>
      original?.url?.includes(p)
    );

    if (status === 401 && !isAuthExempt && !original._retry) {
      original._retry = true; // 무한 재시도 방지
      try {
        // 동시에 여러 요청이 만료돼도 재발급은 1번만
        refreshPromise = refreshPromise ?? api.post('/auth/refresh');
        await refreshPromise;
        refreshPromise = null;
        return api(original); // 원 요청 재시도
      } catch (refreshError) {
        // 재발급도 실패 → 로그인 화면으로
        refreshPromise = null;
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
