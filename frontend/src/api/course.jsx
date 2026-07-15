import api from './axios';

// 선호도 저장 (기간·이동수단·동선·취향 등 코스 생성 조건)
export const savePreferences = (payload) =>
  api.post('/courses/preferences', payload);

// 여행 코스 생성 (AI 연동, 저장은 안 됨 - 재추천 시 동일 preferenceId로 재호출)
export const generateCourse = (preferenceId) =>
  api.post('/courses/generate', { preferenceId });
