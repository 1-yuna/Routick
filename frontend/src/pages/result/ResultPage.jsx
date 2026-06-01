import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DndContext, closestCenter } from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomSheet from '../../common/sheet/BottomSheet.jsx';
import CourseItem from '../../components/result/view/CourseItem.jsx';
import EditCourseItem from '../../components/result/edit/EditCourseItem.jsx';
import DayHeader from '../../components/result/DayHeader.jsx';
import CourseActions from '../../components/result/CourseActions.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import { calcPlaceTimes } from '../../utils/timeUtils.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import CourseList from '../../components/result/view/CourseList.jsx';
import EditCourseList from '../../components/result/edit/EditCourseList.jsx';

export default function ResultPage() {
  const course = useCourseStore((state) => state.course);
  const setCourse = useCourseStore((state) => state.setCourse);
  const deletePlace = useCourseStore((state) => state.deletePlace);
  const reorderPlaces = useCourseStore((state) => state.reorderPlaces);
  const navigate = useNavigate();
  const [sheetY, setSheetY] = useState(400);
  const [selectedDay, setSelectedDay] = useState(1);
  const [isEditing, setIsEditing] = useState(false);
  const [checkedPlaces, setCheckedPlaces] = useState([]);
  const [originalCourse, setOriginalCourse] = useState(null);

  const selectedPlaces = calcPlaceTimes(
    course.find((day) => day.day === selectedDay)?.places || []
  );

  const handleEditStart = () => {
    setOriginalCourse(course);
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    if (originalCourse) {
      setCourse(originalCourse);
    }
    setIsEditing(false);
    setCheckedPlaces([]);
  };

  const handleCheck = (dayIndex, placeIndex) => {
    setCheckedPlaces((prev) => {
      const exists = prev.some(
        (p) => p.dayIndex === dayIndex && p.placeIndex === placeIndex
      );
      return exists
        ? prev.filter(
            (p) => !(p.dayIndex === dayIndex && p.placeIndex === placeIndex)
          )
        : [...prev, { dayIndex, placeIndex }];
    });
  };

  const handleDelete = () => {
    checkedPlaces
      .sort((a, b) => b.placeIndex - a.placeIndex)
      .forEach(({ dayIndex, placeIndex }) => {
        deletePlace(dayIndex, placeIndex);
      });
    setCheckedPlaces([]);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const fromDay = Number(active.id.toString().split('-')[0]);
    const toDay = Number(over.id.toString().split('-')[0]);
    const fromDayIndex = course.findIndex((day) => day.day === fromDay);
    const toDayIndex = course.findIndex((day) => day.day === toDay);

    if (fromDay === toDay) {
      // 같은 day 내 이동
      const places = course[fromDayIndex].places;
      const oldIndex = places.findIndex(
        (p) => `${fromDay}-${p.id}` === active.id
      );
      const newIndex = places.findIndex(
        (p) => `${fromDay}-${p.id}` === over.id
      );
      reorderPlaces(fromDayIndex, arrayMove(places, oldIndex, newIndex));
    } else {
      const fromPlaces = [...course[fromDayIndex].places];
      const toPlaces = [...course[toDayIndex].places];
      const fromIndex = fromPlaces.findIndex(
        (p) => `${fromDay}-${p.id}` === active.id
      );
      const toIndex = toPlaces.findIndex((p) => `${toDay}-${p.id}` === over.id);

      const [movedPlace] = fromPlaces.splice(fromIndex, 1);
      const newId = Date.now(); // 여기 추가
      toPlaces.splice(toIndex, 0, { ...movedPlace, id: newId });

      reorderPlaces(fromDayIndex, fromPlaces);
      reorderPlaces(toDayIndex, toPlaces);
    }
  };

  const handleEditComplete = () => {
    setIsEditing(false);
    setCheckedPlaces([]);
  };

  return (
    <div className="relative w-full h-screen">
      {/*상단 바*/}
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
        {isEditing ? (
          <>
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
            <CourseList
              course={course}
              selectedDay={selectedDay}
              onDaySelect={setSelectedDay}
              onCardClick={(place) =>
                navigate(`/place/${place.id}`, { state: { ...place } })
              }
            />
            <CourseActions
              onAdd={() =>
                navigate('/select/address/search', { state: { mode: 'add' } })
              }
              onEdit={() => handleEditStart()}
              onSave={() => console.log('저장')}
            />
          </div>
        )}
      </BottomSheet>
    </div>
  );
}
