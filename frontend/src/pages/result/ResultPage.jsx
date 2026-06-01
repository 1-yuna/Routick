import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseActions from '../../components/result/CourseActions.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import { calcPlaceTimes } from '../../utils/timeUtils.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import CourseList from '../../components/result/view/CourseList.jsx';
import EditCourseList from '../../components/result/edit/EditCourseList.jsx';
import useCourseEdit from '../../hooks/useCourseEdit.jsx';

// 결과 페이지 - 코스 지도 및 바텀시트로 일정 표시
export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  console.log('course:', course);
  const navigate = useNavigate();
  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);

  const {
    isEditing,
    checkedPlaces,
    handleEditStart,
    handleEditCancel,
    handleEditComplete,
    handleCheck,
    handleDelete,
    handleDragEnd,
  } = useCourseEdit();

  // 선택된 day의 장소 목록 (시간 계산 포함)
  const selectedPlaces = calcPlaceTimes(
    course.find((day) => day.day === selectedDay)?.places || []
  );

  return (
    <div className="relative w-full h-screen">
      {/*상단 바 - 편집 모드면 TopBar, 아니면 MapTopBar*/}
      {isEditing ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={handleEditCancel}
            text="완료"
            className3="text-primary text-16-sb"
            onTextClick={handleEditComplete}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar onClick={() => navigate('/home')} icon={CancelIcon} />
      )}

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
        {isEditing ? (
          <>
            {/*편집 모드 - 드래그 정렬 + 체크박스 삭제*/}
            <EditCourseList
              course={course}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
              checkedPlaces={checkedPlaces}
              onCheck={handleCheck}
              onDragEnd={handleDragEnd}
            />
            {checkedPlaces.length > 0 && (
              <FullWidthButton
                text="삭제하기"
                className="bg-primary rounded-[5px] mt-4"
                onClick={handleDelete}
              />
            )}
          </>
        ) : (
          <div className="flex flex-col gap-12">
            {/*일반 모드 - 코스 리스트*/}
            <CourseList
              course={course}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
              onCardClick={(place) =>
                navigate(`/place/${place.id}`, { state: { ...place } })
              }
            />
            {/*장소 추가 / 편집 / 저장 버튼*/}
            <CourseActions
              onAdd={() =>
                navigate('/select/address/search', { state: { mode: 'add' } })
              }
              onEdit={handleEditStart}
              onSave={() => console.log('저장')}
            />
          </div>
        )}
      </BottomSheet>
    </div>
  );
}
