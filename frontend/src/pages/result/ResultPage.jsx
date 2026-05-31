// pages/result/ResultPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import BottomSheet from '../../components/result/BottomSheet.jsx';
import CourseItem from '../../components/result/CourseItem.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import SampleImage from '../../assets/images/mock/sample.png';

const mockCourse = [
  {
    day: 1,
    places: [
      {
        id: 1,
        time: '09:00',
        endTime: '10:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '도보',
        transportTime: '10분',
        lat: 37.5479,
        lng: 126.9228,
      },
      {
        id: 2,
        time: '20:00',
        endTime: '21:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '자동차',
        transportTime: '15분',
        lat: 37.5574,
        lng: 126.9248,
      },
      {
        id: 3,
        time: '20:00',
        endTime: '21:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '자동차',
        transportTime: '15분',
        lat: 37.5574,
        lng: 126.9248,
      },
    ],
  },
  {
    day: 2,
    places: [
      {
        id: 1,
        time: '09:00',
        endTime: '10:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '도보',
        transportTime: '10분',
        lat: 37.5479,
        lng: 126.9228,
      },
      {
        id: 2,
        time: '20:00',
        endTime: '21:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '자동차',
        transportTime: '15분',
        lat: 37.5574,
        lng: 126.9248,
      },
      {
        id: 3,
        time: '20:00',
        endTime: '21:00',
        name: '타코잇 상수역점',
        rating: 4.6,
        reviewCount: 1243,
        description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
        src: SampleImage,
        transport: '자동차',
        transportTime: '15분',
        lat: 37.5574,
        lng: 126.9248,
      },
    ],
  },
];

export default function ResultPage() {
  const navigate = useNavigate();
  const [sheetY, setSheetY] = useState(400);

  return (
    <div className="relative w-full h-screen">
      {/*상단 바*/}
      <MapTopBar onClick={() => navigate(-1)} />

      {/*지도*/}
      <KakaoMap
        lat={mockCourse[0].places[0].lat}
        lng={mockCourse[0].places[0].lng}
      />

      {/*바텀시트*/}
      <BottomSheet
        sheetY={sheetY}
        setSheetY={setSheetY}
        initialHeight={400}
        snapPoints={[100, 400, 700]}
        maxHeightPercent={75}
      >
        {mockCourse.map((dayData, dayIndex) => (
          <div key={dayData.day}>
            {/*헤더*/}
            <div className="flex py-4 justify-between items-center">
              <p className="text-16-sb text-black1">day {dayData.day}</p>
              {dayIndex === 0 && (
                <button className="text-14-rg text-gray2">새로고침</button>
              )}
            </div>

            {/*코스*/}
            <div>
              {dayData.places.map((place, index) => (
                <CourseItem
                  key={place.id}
                  place={place}
                  isLast={index === dayData.places.length - 1}
                />
              ))}
            </div>
          </div>
        ))}

        {/*버튼*/}
        <div className="flex gap-3 mt-4">
          <button className="flex-1 h-12 rounded-[10px] border border-line2 text-14-sb text-gray2">
            장소 추가
          </button>
          <button className="flex-1 h-12 rounded-[10px] border border-line2 text-14-sb text-gray2">
            편집
          </button>
        </div>
        <FullWidthButton
          text="저장하기"
          className="bg-primary mt-3"
          onClick={() => console.log('저장')}
        />
      </BottomSheet>
    </div>
  );
}
