import api from './axios';

// 여행 장소 이미지 업로드 (저장 시점에 호출, 실제 경로 반환)
export const uploadTripImage = (file) => {
  const formData = new FormData();
  formData.append('image', file);
  return api.post('/images/trip', formData);
};
