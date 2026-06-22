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
// DayHeader로 day 구분, 드래그로 순서 변경
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
          // walk 블록 제외하고 place/parking만 표시
          const visibleBlocks = dayData.blocks.filter(
            (b) => b.type === 'place' || b.type === 'parking'
          );

          // place 순서 카운터
          let placeCount = 0;

          return (
            <div key={dayData.dayNumber}>
              {/* DayHeader */}
              <DayHeader
                day={dayData.dayNumber}
                showRefresh={false}
                isSelected={selectedDay === dayData.dayNumber}
                onClick={() => onDaySelect(dayData.dayNumber)}
              />

              {/* 블록 리스트 */}
              <SortableContext
                items={visibleBlocks.map((b) => b.blockOrder)}
                strategy={verticalListSortingStrategy}
              >
                {visibleBlocks.map((block) => {
                  if (block.type === 'place') placeCount++;
                  const displayIndex =
                    block.type === 'place' ? placeCount : null;

                  return (
                    <EditBlockItem
                      key={block.blockOrder}
                      block={block}
                      index={displayIndex}
                      isChecked={checkedBlocks.includes(block.blockOrder)}
                      onCheck={() => onCheck(block.blockOrder)}
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
