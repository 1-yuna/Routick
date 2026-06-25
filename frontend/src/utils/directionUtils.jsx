import axios from 'axios';

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_REST_API_KEY;

// 도보 이동시간 추정 - 직선거리 기반 (평균 도보 속도 4km/h)
const getWalkTime = (origin, destination) => {
  const R = 6371; // 지구 반지름 (km)
  const dLat = ((destination.lat - origin.lat) * Math.PI) / 180;
  const dLng = ((destination.lng - origin.lng) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((origin.lat * Math.PI) / 180) *
      Math.cos((destination.lat * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const distance = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)); // 직선거리 (km)
  console.log('출발:', origin);
  console.log('도착:', destination);
  console.log('직선거리(km):', distance);
  console.log('계산된 시간(분):', Math.ceil((distance / 4) * 60));
  return Math.ceil((distance / 4) * 60); // 분 단위로 변환
};

// 이동시간 계산 (분 단위 반환)
// - 도보: 직선거리 기반 추정
// - 자동차: 카카오 모빌리티 API 사용
export const getTransportTime = async (origin, destination, transport) => {
  if (transport === '도보') {
    return getWalkTime(origin, destination);
  }
  try {
    const res = await axios.get(
      `https://apis-navi.kakaomobility.com/v1/directions`,
      {
        params: {
          origin: `${origin.lng},${origin.lat}`,
          destination: `${destination.lng},${destination.lat}`,
        },
        headers: { Authorization: `KakaoAK ${KAKAO_API_KEY}` },
      }
    );
    const route = res.data.routes?.[0];
    if (!route || route.result_code !== 0) {
      console.warn(
        '카카오 경로 탐색 실패, 도보 추정값 사용:',
        route?.result_msg
      );
      return getWalkTime(origin, destination);
    }
    return Math.ceil(route.summary.duration / 60);
  } catch (e) {
    console.warn('카카오 API 오류, 도보 추정값 사용:', e);
    return getWalkTime(origin, destination);
  }
};

export const calcAllTransportTimes = async (course) => {
  return Promise.all(
    course.map(async (dayData) => {
      const updatedPlaces = await Promise.all(
        dayData.places.map(async (place, index) => {
          if (index === dayData.places.length - 1) return place;
          const nextPlace = dayData.places[index + 1];
          const transportTime = await getTransportTime(
            { lat: place.lat, lng: place.lng },
            { lat: nextPlace.lat, lng: nextPlace.lng },
            dayData.transport
          );
          return { ...place, transportTime };
        })
      );
      return { ...dayData, places: updatedPlaces };
    })
  );
};
