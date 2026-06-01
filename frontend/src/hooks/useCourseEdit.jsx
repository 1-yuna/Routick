import { useState } from 'react';
import { arrayMove } from '@dnd-kit/sortable';
import useCourseStore from '../store/courseStore.jsx';

// 코스 편집 관련 로직 (체크박스 삭제, 드래그 순서 변경, 편집 취소/완료)
export default function useCourseEdit() {
  const course = useCourseStore((state) => state.course);
  const setCourse = useCourseStore((state) => state.setCourse);
  const deletePlace = useCourseStore((state) => state.deletePlace);
  const reorderPlaces = useCourseStore((state) => state.reorderPlaces);

  const [isEditing, setIsEditing] = useState(false);
  const [checkedPlaces, setCheckedPlaces] = useState([]);
  const [originalCourse, setOriginalCourse] = useState(null); // 편집 취소 시 복원용

  // 편집 시작 - 원본 코스 저장
  const handleEditStart = () => {
    setOriginalCourse(course);
    setIsEditing(true);
  };

  // 편집 취소 - 원본 코스로 복원
  const handleEditCancel = () => {
    if (originalCourse) setCourse(originalCourse);
    setIsEditing(false);
    setCheckedPlaces([]);
  };

  // 편집 완료
  const handleEditComplete = () => {
    setIsEditing(false);
    setCheckedPlaces([]);
  };

  // 체크 토글
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

  // 체크된 장소 삭제
  const handleDelete = () => {
    checkedPlaces
      .sort((a, b) => b.placeIndex - a.placeIndex)
      .forEach(({ dayIndex, placeIndex }) => deletePlace(dayIndex, placeIndex));
    setCheckedPlaces([]);
  };

  // 드래그 종료 - 같은 day 내 또는 day 간 순서 변경
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
      // 다른 day 간 이동
      const fromPlaces = [...course[fromDayIndex].places];
      const toPlaces = [...course[toDayIndex].places];
      const fromIndex = fromPlaces.findIndex(
        (p) => `${fromDay}-${p.id}` === active.id
      );
      const toIndex = toPlaces.findIndex((p) => `${toDay}-${p.id}` === over.id);

      const [movedPlace] = fromPlaces.splice(fromIndex, 1);
      toPlaces.splice(toIndex, 0, { ...movedPlace, id: Date.now() });

      reorderPlaces(fromDayIndex, fromPlaces);
      reorderPlaces(toDayIndex, toPlaces);
    }
  };

  return {
    isEditing,
    checkedPlaces,
    handleEditStart,
    handleEditCancel,
    handleEditComplete,
    handleCheck,
    handleDelete,
    handleDragEnd,
  };
}
