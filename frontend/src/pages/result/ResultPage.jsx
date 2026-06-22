import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseActions from '../../components/result/view/CourseActions.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import CourseList from '../../components/result/view/CourseList.jsx';
import SaveCompleteModal from '../../components/result/save/SaveCompleteModal.jsx';
import TitleInputModal from '../../components/result/save/TitleInputModal.jsx';
import { extractMarkers } from '../../utils/markerUtils.jsx';

export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  const navigate = useNavigate();
  const location = useLocation();
  const fromMyTrip = location.state?.from === 'mytrip';
  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const selectedDayData = course.days.find((d) => d.dayNumber === selectedDay);
  const selectedBlocks = selectedDayData?.blocks ?? [];
  const mapMarkers = extractMarkers(selectedBlocks);

  const handleSave = () => {
    setShowTitleModal(false);
    setShowSaveModal(true);
  };

  return (
    <div className="relative w-full h-screen">
      {showTitleModal && (
        <TitleInputModal
          onConfirm={handleSave}
          onCancel={() => setShowTitleModal(false)}
        />
      )}
      {showSaveModal && (
        <SaveCompleteModal onConfirm={() => navigate('/home')} />
      )}

      {isEditing ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={() => setIsEditing(false)}
            text="완료"
            className3="text-primary text-16-sb"
            onTextClick={() => setIsEditing(false)}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar
          onClick={() => (fromMyTrip ? navigate(-1) : navigate('/home'))}
          icon={fromMyTrip ? LeftIcon : CancelIcon}
        />
      )}

      <KakaoMap places={mapMarkers} padding={[50, 50, sheetY + 50, 50]} />

      <BottomSheet
        sheetY={sheetY}
        setSheetY={setSheetY}
        initialHeight={400}
        snapPoints={[100, 400, 700]}
        maxHeightPercent={75}
        footer={null}
      >
        <div className="flex flex-col gap-8">
          <CourseList
            course={course}
            selectedDay={selectedDay}
            onDaySelect={setSelectedDay}
            onCardClick={(block) =>
              navigate(`/place/${block.placeId}`, { state: { ...block } })
            }
          />
          <CourseActions
            onAdd={() =>
              navigate('/select/address/search', { state: { mode: 'add' } })
            }
            onEdit={() => setIsEditing(true)}
            onSave={() => setShowTitleModal(true)}
          />
        </div>
      </BottomSheet>
    </div>
  );
}
