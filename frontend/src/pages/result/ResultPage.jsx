// pages/result/ResultPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseItem from '../../components/result/CourseItem.jsx';
import SampleImage from '../../assets/images/mock/sample.png';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import DayHeader from '../../components/result/DayHeader.jsx';
import CourseActions from '../../components/result/CourseActions.jsx';

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
        category: 'food',
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
        category: 'lodging',
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
      <MapTopBar onClick={() => navigate(-1)} icon={CancelIcon} />

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
        {/*바텀시트 바디*/}
        <div className="flex flex-col gap-12">
          {mockCourse.map((dayData, dayIndex) => (
            <div key={dayData.day}>
              {/*헤더*/}
              <DayHeader day={dayData.day} showRefresh={dayIndex === 0} />

              {/*코스*/}
              <div>
                {dayData.places.map((place, index) => (
                  <CourseItem
                    key={place.id}
                    place={place}
                    isLast={index === dayData.places.length - 1}
                    onCardClick={() => navigate(`/place/${place.id}`)}
                  />
                ))}
              </div>
            </div>
          ))}

          {/*버튼*/}
          <CourseActions
            onAdd={() => console.log('장소 추가')}
            onEdit={() => console.log('편집')}
            onSave={() => console.log('저장')}
          />
        </div>
      </BottomSheet>
    </div>
  );
}
