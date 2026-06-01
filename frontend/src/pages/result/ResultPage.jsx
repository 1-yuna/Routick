// pages/result/ResultPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseItem from '../../components/result/CourseItem.jsx';
import DayHeader from '../../components/result/DayHeader.jsx';
import CourseActions from '../../components/result/CourseActions.jsx';
import { calcPlaceTimes } from '../../utils/timeUtils.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import useCourseStore from '../../store/courseStore.jsx';

// 결과 페이지 - 코스 지도 및 바텀시트로 일정 표시
export default function ResultPage() {
  // 코스 데이터
  const course = useCourseStore((state) => state.course);
  const navigate = useNavigate();
  const [sheetY, setSheetY] = useState(400); // 바텀시트 높이
  const [selectedDay, setSelectedDay] = useState(1); // 선택된 day

  // 선택된 day의 장소 목록 (시간 계산 포함)
  const selectedPlaces = calcPlaceTimes(
    course.find((day) => day.day === selectedDay)?.places || []
  );

  return (
    <div className="relative w-full h-screen">
      {/*상단 바*/}
      <MapTopBar onClick={() => navigate('/home')} icon={CancelIcon} />

      {/*지도 - 선택된 day의 장소 마커 및 동선 표시*/}
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

              {/*코스 리스트*/}
              <div>
                {calcPlaceTimes(dayData.places).map((place, index) => (
                  <CourseItem
                    key={index}
                    index={index}
                    place={place}
                    transport={dayData.transport}
                    isLast={index === dayData.places.length - 1}
                    onCardClick={() =>
                      navigate(`/place/${place.id}`, { state: { ...place } })
                    }
                  />
                ))}
              </div>
            </div>
          ))}

          {/*장소 추가 / 편집 / 저장 버튼*/}
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
