import axios from 'axios';

// 공용 axios 인스턴스
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // http://localhost:8080/api/v1
  withCredentials: true, // httpOnly 쿠키 전송 필수
});

// 401 처리: accessToken 만료(TOKEN_EXPIRED)면 재발급 후 원 요청 1회 재시도
let refreshPromise = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const code = error.response?.data?.code;

    if (status === 401 && code === 'TOKEN_EXPIRED' && !original._retry) {
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
