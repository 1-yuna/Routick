import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseActions from '../../components/result/view/CourseActions.jsx';
import CourseList from '../../components/result/view/CourseList.jsx';
import EditBlockList from '../../components/result/edit/EditBlockList.jsx';
import SaveCompleteModal from '../../components/result/save/SaveCompleteModal.jsx';
import TitleInputModal from '../../components/result/save/TitleInputModal.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import BaseModal from '../../common/modal/BaseModal.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import { extractMarkers } from '../../utils/markerUtils.jsx';

export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  const deleteBlocks = useCourseStore((state) => state.deleteBlocks);
  const reorderBlocks = useCourseStore((state) => state.reorderBlocks);
  const navigate = useNavigate();
  const location = useLocation();
  const fromMyTrip = location.state?.from === 'mytrip';

  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [checkedBlocks, setCheckedBlocks] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const selectedDayData = course.days.find((d) => d.dayNumber === selectedDay);
  const selectedBlocks = selectedDayData?.blocks ?? [];
  const mapMarkers = extractMarkers(selectedBlocks);

  const handleSave = () => {
    setShowTitleModal(false);
    setShowSaveModal(true);
  };

  const handleCheck = (uniqueId) => {
    setCheckedBlocks((prev) =>
      prev.includes(uniqueId)
        ? prev.filter((b) => b !== uniqueId)
        : [...prev, uniqueId]
    );
  };

  const handleEditDone = () => {
    setIsEditing(false);
    setCheckedBlocks([]);
  };

  // reordered: EditBlockList에서 이미 arrayMove 적용된 visible 블록 배열
  const handleDragEnd = (event, dayNumber, reordered) => {
    const dayData = course.days.find((d) => d.dayNumber === dayNumber);
    if (!dayData) return;

    // walk 블록은 visible 블록 사이에 다시 끼워넣기
    const walkBlocks = dayData.blocks.filter((b) => b.type === 'walk');
    const newBlocks = [];
    reordered.forEach((block, idx) => {
      newBlocks.push(block);
      if (idx < reordered.length - 1 && walkBlocks[idx]) {
        newBlocks.push(walkBlocks[idx]);
      }
    });

    reorderBlocks(dayNumber, newBlocks);
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
      {showDeleteModal && (
        <BaseModal
          onConfirm={() => {
            deleteBlocks(checkedBlocks);
            setCheckedBlocks([]);
            setShowDeleteModal(false);
          }}
          onCancel={() => setShowDeleteModal(false)}
        >
          <p className="text-14-sb text-black1">이 장소를 삭제하시겠습니까?</p>
          <p className="text-12-rg text-gray2">일정에서 바로 삭제돼요</p>
        </BaseModal>
      )}

      {/* 상단 바 */}
      {isEditing ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={handleEditDone}
            text="완료"
            className3="text-primary text-16-sb"
            onTextClick={handleEditDone}
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
        footer={
          isEditing && checkedBlocks.length > 0 ? (
            <FullWidthButton
              text="삭제하기"
              className="bg-primary"
              onClick={() => setShowDeleteModal(true)}
            />
          ) : null
        }
      >
        {isEditing ? (
          <EditBlockList
            course={course}
            selectedDay={selectedDay}
            onDaySelect={setSelectedDay}
            checkedBlocks={checkedBlocks}
            onCheck={handleCheck}
            onDragEnd={handleDragEnd}
          />
        ) : (
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
                navigate('/select/address/search', {
                  state: { mode: 'add', dayNumber: selectedDay },
                })
              }
              onEdit={() => setIsEditing(true)}
              onSave={() => setShowTitleModal(true)}
            />
          </div>
        )}
      </BottomSheet>
    </div>
  );
}
