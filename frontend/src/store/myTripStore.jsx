import { create } from 'zustand';
import SampleImage from '../assets/images/mock/sample.png';

// TODO: API 연동 시 제거
const mockTrips = [
  {
    id: 1,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑', '즐겁다'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 2,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '배고프다다'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 3,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 4,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 5,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 6,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 7,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
];

// 내 여행 전역 상태 관리
const useMyTripStore = create((set) => ({
  trips: mockTrips,

  // 여행 삭제
  deleteTrips: (ids) =>
    set((state) => ({
      trips: state.trips.filter((trip) => !ids.includes(trip.id)),
    })),

  // 여행 이미지 변경
  updateTripImage: (id, imageUrl) =>
    set((state) => ({
      trips: state.trips.map((trip) =>
        trip.id === id ? { ...trip, src: imageUrl } : trip
      ),
    })),

  // 여행 제목 변경
  updateTripTitle: (id, title) =>
    set((state) => ({
      trips: state.trips.map((trip) =>
        trip.id === id ? { ...trip, title } : trip
      ),
    })),
}));

export default useMyTripStore;
