import api from './axios';

// 장소 상세 조회 (놀거리 카드·지역추천 카드 클릭 시 상세 정보 보강용)
export const getPlaceDetail = (placeId) => api.get(`/places/${placeId}`);

// 지역추천 TOP5 조회
export const getRecommendations = (regionName, lat, lng) =>
  api.get('/places/recommendations', { params: { regionName, lat, lng } });

// 놀거리 카테고리별 조회
export const getPlaceList = (category, regionName, lat, lng) =>
  api.get('/places/list', { params: { category, regionName, lat, lng } });
