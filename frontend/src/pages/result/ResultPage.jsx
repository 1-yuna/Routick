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
import useMyTripStore from '../../store/myTripStore.jsx';
import { extractMarkers } from '../../utils/markerUtils.jsx';
import { recalcTransportUtils } from '../../utils/recalcTransportUtils.jsx';

export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  const addTrip = useMyTripStore((state) => state.addTrip);
  const deleteBlocks = useCourseStore((state) => state.deleteBlocks);
  const updateBlocks = useCourseStore((state) => state.updateBlocks);
  const navigate = useNavigate();
  const location = useLocation();
  const fromMyTrip = location.state?.from === 'mytrip';

  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const isEditing = useCourseStore((state) => state.isEditing);
  const setIsEditing = useCourseStore((state) => state.setIsEditing);
  const [checkedBlocks, setCheckedBlocks] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  // 순서변경 임시 저장 - 완료 누를 때만 store 반영
  const [pendingLocalDays, setPendingLocalDays] = useState(null);

  const selectedDayData = course.days.find((d) => d.dayNumber === selectedDay);
  const selectedBlocks = selectedDayData?.blocks ?? [];

  // 편집 모드에서 pendingLocalDays 있으면 그 기준으로 마커 계산
  const pendingDayData = pendingLocalDays?.find(
    (d) => d.dayNumber === selectedDay
  );
  const pendingBlocks = pendingDayData
    ? pendingDayData.blocks.map(({ _uid, ...rest }) => rest)
    : null;
  const mapMarkers = extractMarkers(
    pendingBlocks ?? selectedBlocks,
    selectedDayData
  );

  const handleSave = (title) => {
    const days = course.days ?? [];
    const startRegion = days[0]?.start?.name ?? '';
    const endRegion = days[days.length - 1]?.end?.name ?? '';
    const region =
      startRegion === endRegion ? startRegion : `${startRegion} → ${endRegion}`;

    const meta = course.meta ?? {};

    addTrip({
      title: title?.trim() || '나의 여행',
      region,
      transport: course.transport === 'car' ? '자동차' : '도보',
      // 카드 태그: 분위기 + 활동
      tags: [...(meta.mood ?? []), ...(meta.activity ?? [])],
      // 해시태그: 동행자, 기간
      hashtags: [meta.companion, meta.period].filter(Boolean),
      course, // 코스 전체 저장
    });
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

  // 완료 버튼 - 전체 재계산 (장소간 거리, 번호, 시작시간 09:00 고정)
  const handleEditDone = async () => {
    const source = pendingLocalDays ?? course.days;

    for (const localDay of source) {
      const dayData = course.days.find(
        (d) => d.dayNumber === localDay.dayNumber
      );
      if (!dayData) continue;

      // pendingLocalDays는 place/parking만 있음 (_uid 제거)
      // walk는 recalc가 알아서 재삽입하므로 visible 블록만 추림
      const visibleBlocks = localDay.blocks
        .filter((b) => b.type === 'place' || b.type === 'parking')
        .map(({ _uid, ...rest }) => rest);

      const recalculated = await recalcTransportUtils(
        visibleBlocks,
        course.transport
      );
      updateBlocks(localDay.dayNumber, recalculated);
    }

    setIsEditing(false);
    setCheckedBlocks([]);
    setPendingLocalDays(null);
  };

  // 뒤로가기 버튼 - 순서변경 취소 (store 반영 안 함)
  const handleEditCancel = () => {
    setIsEditing(false);
    setCheckedBlocks([]);
    setPendingLocalDays(null);
  };

  // 드래그 중/종료 - store 반영 안 하고 pendingLocalDays에만 저장
  // 완료 버튼 눌러야 store 반영
  const handleDragEnd = (newLocalDays) => {
    setPendingLocalDays(newLocalDays);
  };

  const handleDragMove = (newLocalDays) => {
    setPendingLocalDays(newLocalDays);
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

      {showExitModal && (
        <BaseModal
          onConfirm={() => navigate('/home')}
          onCancel={() => setShowExitModal(false)}
        >
          <p className="text-14-sb text-black1">이 화면을 나가시겠어요?</p>
          <p className="text-12-rg text-gray2">
            저장하지 않으면 이 일정은 사라져요
          </p>
        </BaseModal>
      )}

      {/* 상단 바 */}
      {isEditing ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={handleEditCancel}
            text="완료"
            className3="text-primary text-16-sb"
            onTextClick={handleEditDone}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar
          onClick={() => (fromMyTrip ? navigate(-1) : setShowExitModal(true))}
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
            onDragMove={handleDragMove}
          />
        ) : (
          <div className="flex flex-col gap-8">
            <CourseList
              course={course}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
              onCardClick={(block) =>
                navigate(`/place/${block.placeId}`, {
                  state: { ...block, from: fromMyTrip ? 'mytrip' : 'result' },
                })
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
