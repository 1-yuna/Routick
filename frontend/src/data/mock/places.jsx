import SampleImage from '../../assets/images/mock/sample.png';

// TODO: API 연동 시 제거
export const mockPlaces = Array.from({ length: 10 }, (_, i) => ({
  id: i + 1,
  name: '타코잇 상수역점',
  description:
    '우리의 추억을 그림으로 기록하기! 정해진 도안 없이 자유롭게 백드롭 페인팅을 체험하는 드로잉 카페',
  address: '경기 고양시 덕양구 동산동 370',
  src: SampleImage,
  lat: 37.5479 + i * 0.001,
  lng: 126.9228 + i * 0.001,
  placeId: `mock-place-${i + 1}`,
}));
