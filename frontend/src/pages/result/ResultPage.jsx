import { useEffect, useState } from 'react';
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
import { recalcTransportUtils } from '../../utils/recalcTransportUtils.jsx';
import { createTrip, updateTripDays } from '../../api/trip.jsx';
import { generateCourse } from '../../api/course.jsx';
import {
  buildTripCreatePayload,
  buildTripDaysUpdatePayload,
} from '../../utils/tripUtils.jsx';
import { normalizeCourse } from '../../utils/courseUtils.jsx';

// 언마운트돼도 유지되는 화면 상태 (장소 상세로 갔다가 돌아와도 고정되게)
let resultSheetY = 400;
let resultSelectedDay = 1;
let resultScrollTop = 0;

export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  const setCourse = useCourseStore((state) => state.setCourse);
  const preferenceId = useCourseStore((state) => state.preferenceId);
  const deleteBlocks = useCourseStore((state) => state.deleteBlocks);
  const updateBlocks = useCourseStore((state) => state.updateBlocks);
  const navigate = useNavigate();
  const location = useLocation();
  const fromMyTrip = location.state?.from === 'mytrip';

  const [sheetY, setSheetY] = useState(resultSheetY);
  const [selectedDay, setSelectedDay] = useState(resultSelectedDay);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const isEditing = useCourseStore((state) => state.isEditing);
  const setIsEditing = useCourseStore((state) => state.setIsEditing);
  const [checkedBlocks, setCheckedBlocks] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  // 순서변경 임시 저장 - 완료 누를 때만 store 반영
  const [pendingLocalDays, setPendingLocalDays] = useState(null);
  // 재추천 로딩 상태 - true인 동안 바텀시트에 로딩 애니메이션 표시
  const [isRefreshing, setIsRefreshing] = useState(false);

  // sheetY/selectedDay 바뀔 때마다 모듈 변수에 동기화 (setState 호출 아니라서 lint 규칙 안 걸림)
  useEffect(() => {
    resultSheetY = sheetY;
  }, [sheetY]);

  useEffect(() => {
    resultSelectedDay = selectedDay;
  }, [selectedDay]);

  const selectedDayData = course.days.find((d) => d.dayNumber === selectedDay);
  const selectedBlocks = selectedDayData?.blocks ?? [];

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

  // 저장 (새로 생성한 코스 - POST /trips)
  const handleSave = async (title) => {
    try {
      const payload = buildTripCreatePayload(course, title);
      await createTrip(payload);
      setShowTitleModal(false);
      setShowSaveModal(true);
    } catch (e) {
      setShowTitleModal(false);
      alert('저장에 실패했어요. 다시 시도해주세요.');
    }
  };

  // 수정 (저장된 여행 - PUT /trips/{tripId}/days), 제목은 이미 있으므로 모달 없이 바로 호출
  const handleUpdateTrip = async () => {
    try {
      const payload = buildTripDaysUpdatePayload(course);
      await updateTripDays(course.tripId, payload);
      setShowUpdateModal(true);
    } catch (e) {
      alert('수정에 실패했어요. 다시 시도해주세요.');
    }
  };

  // 재추천 - *(fix)* savePreferences를 다시 호출하면 안 됨. 최초 생성(LoadingPage)
  // 때 저장해둔 동일 preferenceId로 generateCourse만 재호출
  // (course.jsx 주석: "재추천 시 동일 preferenceId로 재호출" —
  //  이전에 savePreferences를 재호출하도록 만들었을 때 POST /courses/preferences
  //  400 Bad Request가 났던 원인)
  const handleRefresh = async () => {
    if (isRefreshing) return;
    if (!preferenceId) {
      alert(
        '재추천에 필요한 정보를 찾을 수 없어요. 처음부터 다시 시도해주세요.'
      );
      return;
    }
    setIsRefreshing(true);
    try {
      const courseRes = await generateCourse(preferenceId);
      const newCourse = normalizeCourse(courseRes.data.data);

      setCourse(newCourse);
      // 새 코스의 day 구성이 다를 수 있으니 선택된 day를 첫 day로 리셋
      setSelectedDay(newCourse.days?.[0]?.dayNumber ?? 1);
      setPendingLocalDays(null);
    } catch (e) {
      alert('재추천에 실패했어요. 다시 시도해주세요.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleCheck = (uniqueId) => {
    setCheckedBlocks((prev) =>
      prev.includes(uniqueId)
        ? prev.filter((b) => b !== uniqueId)
        : [...prev, uniqueId]
    );
  };

  const handleEditDone = async () => {
    const source = pendingLocalDays ?? course.days;

    for (const localDay of source) {
      const dayData = course.days.find(
        (d) => d.dayNumber === localDay.dayNumber
      );
      if (!dayData) continue;

      const visibleBlocks = localDay.blocks
        .filter((b) => b.type === 'place' || b.type === 'parking')
        .map(({ _uid, ...rest }) => rest);

      const startBlock = dayData.start
        ? {
            type: 'place',
            lat: dayData.start.lat,
            lng: dayData.start.lng,
            _isAnchor: true,
          }
        : null;
      const endBlock = dayData.end
        ? {
            type: 'place',
            lat: dayData.end.lat,
            lng: dayData.end.lng,
            _isAnchor: true,
          }
        : null;

      const blocksWithAnchors = [
        ...(startBlock ? [startBlock] : []),
        ...visibleBlocks,
        ...(endBlock ? [endBlock] : []),
      ];

      const recalculated = await recalcTransportUtils(
        blocksWithAnchors,
        course.transport
      );

      const withoutAnchors = recalculated
        .filter((b) => !b._isAnchor)
        .map((block, idx) => ({ ...block, blockOrder: idx + 1 }));

      updateBlocks(localDay.dayNumber, withoutAnchors);
    }

    setIsEditing(false);
    setCheckedBlocks([]);
    setPendingLocalDays(null);
  };

  const handleEditCancel = () => {
    setIsEditing(false);
    setCheckedBlocks([]);
    setPendingLocalDays(null);
  };

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
      {showUpdateModal && (
        <BaseModal confirmOnly onConfirm={() => navigate('/mytrip')}>
          <p className="text-14-sb text-black1">수정되었습니다</p>
        </BaseModal>
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
          onConfirm={() => navigate(fromMyTrip ? -1 : '/home')}
          onCancel={() => setShowExitModal(false)}
        >
          <p className="text-14-sb text-black1">
            {fromMyTrip
              ? '수정하지 않고 나가시겠어요?'
              : '이 화면을 나가시겠어요?'}
          </p>
          <p className="text-12-rg text-gray2">
            {fromMyTrip
              ? '수정하지 않으면 변경사항이 사라져요'
              : '저장하지 않으면 이 일정은 사라져요'}
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
          onClick={() => setShowExitModal(true)}
          icon={fromMyTrip ? LeftIcon : CancelIcon}
        />
      )}

      <KakaoMap
        places={mapMarkers}
        padding={[50, 50, sheetY + 50, 50]}
        onMarkerClick={(marker) => {
          const dayData = course.days.find((d) => d.dayNumber === selectedDay);
          if (marker.type === 'place') {
            const block = selectedBlocks.find(
              (b) => b.type === 'place' && String(b.placeOrder) === marker.label
            );
            if (block) {
              navigate(`/place/${block.placeId}`, {
                state: { ...block, from: fromMyTrip ? 'mytrip' : 'result' },
              });
            }
          } else if (marker.type === 'parking') {
            const block = selectedBlocks.find((b) => b.type === 'parking');
            if (block) {
              navigate(`/place/${block.placeId}`, {
                state: { ...block, from: fromMyTrip ? 'mytrip' : 'result' },
              });
            }
          } else if (marker.type === 'start') {
            const point = dayData?.start;
            if (point) {
              navigate(`/place/${encodeURIComponent(point.name)}`, {
                state: { ...point, from: fromMyTrip ? 'mytrip' : 'result' },
              });
            }
          } else if (marker.type === 'end') {
            const point = dayData?.end;
            if (point) {
              navigate(`/place/${encodeURIComponent(point.name)}`, {
                state: { ...point, from: fromMyTrip ? 'mytrip' : 'result' },
              });
            }
          }
        }}
      />

      <BottomSheet
        sheetY={sheetY}
        setSheetY={setSheetY}
        initialHeight={400}
        snapPoints={[100, 400, 700]}
        maxHeightPercent={75}
        initialScrollTop={resultScrollTop}
        onContentScroll={(top) => {
          resultScrollTop = top;
        }}
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
        ) : isRefreshing ? (
          // 재추천 로딩 - TopCardSection의 "..." bounce 애니메이션과 동일한 스타일
          <div className="flex flex-col items-center justify-center gap-3 py-24">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" />
            </div>
            <p className="text-12-rg text-gray2">
              새로운 코스를 다시 찾고 있어요 ✈️
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            <CourseList
              course={course}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
              onRefresh={handleRefresh}
              onCardClick={(block) =>
                navigate(`/place/${block.placeId}`, {
                  state: { ...block, from: fromMyTrip ? 'mytrip' : 'result' },
                })
              }
              onPointClick={(point) =>
                navigate(`/place/${encodeURIComponent(point.name)}`, {
                  state: { ...point, from: fromMyTrip ? 'mytrip' : 'result' },
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
              onSave={
                fromMyTrip ? handleUpdateTrip : () => setShowTitleModal(true)
              }
              saveLabel={fromMyTrip ? '수정하기' : '저장하기'}
            />
          </div>
        )}
      </BottomSheet>
    </div>
  );
}
