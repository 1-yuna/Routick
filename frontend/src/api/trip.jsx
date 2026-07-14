import api from './axios';

// 여행 저장
export const createTrip = (payload) => api.post('/trips', payload);

// 내 여행 목록 조회
export const getTrips = () => api.get('/trips');

// 내 여행 상세 조회
export const getTripDetail = (tripId) => api.get(`/trips/${tripId}`);

// 여행 수정 (제목/대표이미지, multipart)
export const updateTrip = (tripId, title, coverImageFile) => {
  const formData = new FormData();
  if (title !== undefined && title !== null) formData.append('title', title);
  if (coverImageFile) formData.append('coverImage', coverImageFile);
  return api.patch(`/trips/${tripId}`, formData);
};

// 여행 삭제
export const deleteTrip = (tripId) => api.delete(`/trips/${tripId}`);
