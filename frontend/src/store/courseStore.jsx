// store/courseStore.jsx
import { create } from 'zustand';
import SampleImage from '../assets/images/mock/sample.png';

const mockCourse = [
  {
    day: 1,
    places: [
      {
        id: 1,
        category: 'food',
        stayTime: 120,
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '도보',
        transportTime: 10,
        lat: 37.5479,
        lng: 126.9228,
      },
      {
        id: 2,
        category: 'lodging',
        stayTime: 120,
        name: '스타벅스 합정점',
        rating: 4.2,
        reviewCount: 832,
        description: '한강뷰가 보이는 분위기 좋은 카페',
        src: SampleImage,
        transport: '도보',
        transportTime: 15,
        lat: 37.5497,
        lng: 126.9143,
      },
      {
        id: 3,
        category: 'food',
        stayTime: 120,
        name: '홍대 놀이터',
        rating: 4.0,
        reviewCount: 512,
        description: '홍대 특유의 젊고 활기찬 분위기',
        src: SampleImage,
        lat: 37.5564,
        lng: 126.9238,
      },
    ],
  },
  {
    day: 2,
    places: [
      {
        id: 1,
        category: 'food',
        stayTime: 60,
        name: '연남동 카페거리',
        rating: 4.5,
        reviewCount: 1023,
        description: '감성적인 카페들이 모여있는 거리',
        src: SampleImage,
        transport: '도보',
        transportTime: 10,
        lat: 37.5617,
        lng: 126.9237,
      },
      {
        id: 2,
        category: 'lodging',
        stayTime: 120,
        name: '망원한강공원',
        rating: 4.7,
        reviewCount: 2341,
        description: '한강을 바라보며 쉬어가기 좋은 공원',
        src: SampleImage,
        transport: '자동차',
        transportTime: 15,
        lat: 37.5537,
        lng: 126.9008,
      },
      {
        id: 3,
        category: 'food',
        stayTime: 120,
        name: '합정역 맛집거리',
        rating: 4.3,
        reviewCount: 743,
        description: '다양한 맛집들이 모여있는 거리',
        src: SampleImage,
        transport: '도보',
        transportTime: 10,
        lat: 37.5496,
        lng: 126.9143,
      },
    ],
  },
];

const useCourseStore = create((set) => ({
  course: mockCourse,

  addPlace: (place) =>
    set((state) => ({
      course: state.course.map((day, index) =>
        index === 0 ? { ...day, places: [...day.places, place] } : day
      ),
    })),

  reset: () => set({ course: mockCourse }),
}));

export default useCourseStore;
