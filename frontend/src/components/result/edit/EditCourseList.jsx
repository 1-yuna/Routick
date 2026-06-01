// components/result/EditCourseList.jsx
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import EditCourseItem from './EditCourseItem.jsx';
import DayHeader from '../DayHeader.jsx';

// 편집 모드 - 드래그 정렬 + 체크박스 삭제
export default function EditCourseList({
  course,
  selectedDay,
  onDaySelect,
  checkedPlaces,
  onCheck,
  onDragEnd,
}) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    })
  );

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={onDragEnd}
    >
      <div className="flex flex-col gap-12">
        {course.map((dayData, dayIndex) => (
          <div key={dayData.day}>
            <DayHeader
              day={dayData.day}
              showRefresh={false}
              isSelected={selectedDay === dayData.day}
              onClick={() => onDaySelect(dayData.day)}
            />
            <SortableContext
              items={dayData.places.map((p) => `${dayData.day}-${p.id}`)}
              strategy={verticalListSortingStrategy}
            >
              {dayData.places.map((place, index) => (
                <EditCourseItem
                  key={`${dayData.day}-${place.id}`}
                  place={{ ...place, uniqueId: `${dayData.day}-${place.id}` }}
                  index={index}
                  isChecked={checkedPlaces.some(
                    (p) => p.dayIndex === dayIndex && p.placeIndex === index
                  )}
                  onCheck={() => onCheck(dayIndex, index)}
                />
              ))}
            </SortableContext>
          </div>
        ))}
      </div>
    </DndContext>
  );
}
