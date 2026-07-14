import api from './axios';

// 여행 저장
export const createTrip = (payload) => api.post('/trips', payload);

// 내 여행 목록 조회
export const getTrips = () => api.get('/trips');

// 내 여행 상세 조회
export const getTripDetail = (tripId) => api.get(`/trips/${tripId}`);
