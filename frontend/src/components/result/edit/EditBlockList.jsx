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
import EditBlockItem from './EditBlockItem.jsx';
import DayHeader from '../DayHeader.jsx';

// 편집 모드 - 전체 블록 리스트
// walk 블록은 표시 안 함 (place/parking만 표시)
export default function EditBlockList({
  course,
  selectedDay,
  onDaySelect,
  checkedBlocks,
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
      <div className="flex flex-col gap-8">
        {course.days.map((dayData) => {
          const visibleBlocks = dayData.blocks.filter(
            (b) => b.type === 'place' || b.type === 'parking'
          );

          let placeCount = 0;

          // 유니크 id: `${dayNumber}-${blockOrder}`
          const uniqueIds = visibleBlocks.map(
            (b) => `${dayData.dayNumber}-${b.blockOrder}`
          );

          return (
            <div key={dayData.dayNumber}>
              <DayHeader
                day={dayData.dayNumber}
                showRefresh={false}
                isSelected={selectedDay === dayData.dayNumber}
                onClick={() => onDaySelect(dayData.dayNumber)}
              />

              <SortableContext
                items={uniqueIds}
                strategy={verticalListSortingStrategy}
              >
                {visibleBlocks.map((block) => {
                  if (block.type === 'place') placeCount++;
                  const uniqueId = `${dayData.dayNumber}-${block.blockOrder}`;

                  return (
                    <EditBlockItem
                      key={uniqueId}
                      uniqueId={uniqueId}
                      block={block}
                      index={block.type === 'place' ? placeCount : null}
                      isChecked={checkedBlocks.includes(uniqueId)}
                      onCheck={() => onCheck(uniqueId)}
                    />
                  );
                })}
              </SortableContext>
            </div>
          );
        })}
      </div>
    </DndContext>
  );
}
