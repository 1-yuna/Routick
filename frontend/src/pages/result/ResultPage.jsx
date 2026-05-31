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
import useCourseStore from '../../store/courseStore.jsx';

export default function ResultPage() {
  // 코스 데이터
  const course = useCourseStore((state) => state.course);
  const navigate = useNavigate();
  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);

  const selectedPlaces =
    course.find((day) => day.day === selectedDay)?.places || [];

  return (
    <div className="relative w-full h-screen">
      {/*상단 바*/}
      <MapTopBar onClick={() => navigate(-1)} icon={CancelIcon} />

      {/*지도*/}
      <KakaoMap places={selectedPlaces} padding={[50, 50, sheetY + 50, 50]} />

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
          {course.map((dayData, dayIndex) => (
            <div key={dayData.day}>
              {/*헤더*/}
              <DayHeader
                day={dayData.day}
                showRefresh={dayIndex === 0}
                isSelected={selectedDay === dayData.day}
                onClick={() => setSelectedDay(dayData.day)}
              />

              {/*코스*/}
              <div>
                {dayData.places.map((place, index) => (
                  <CourseItem
                    key={index}
                    index={index}
                    place={place}
                    isLast={index === dayData.places.length - 1}
                    onCardClick={() =>
                      navigate(`/place/${place.id}`, { state: { ...place } })
                    }
                  />
                ))}
              </div>
            </div>
          ))}

          {/*버튼*/}
          <CourseActions
            onAdd={() =>
              navigate('/select/address/search', { state: { mode: 'add' } })
            }
            onEdit={() => console.log('편집')}
            onSave={() => console.log('저장')}
          />
        </div>
      </BottomSheet>
    </div>
  );
}
