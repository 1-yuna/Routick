import { create } from 'zustand';
import SampleImage from '../assets/images/mock/sample.png';
import { mockTrips } from '../data/mock/trips.jsx';

// 내 여행 전역 상태 관리
const useMyTripStore = create((set) => ({
  trips: mockTrips,
  // trips: [],

  // 여행 저장 (현재 코스를 내 여행에 추가)
  addTrip: (trip) =>
    set((state) => ({
      trips: [
        {
          id: Date.now(),
          src: SampleImage,
          ...trip,
        },
        ...state.trips,
      ],
    })),

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
