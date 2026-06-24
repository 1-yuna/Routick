import { useState, useEffect } from 'react';
import {
  DndContext,
  rectIntersection,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import EditBlockItem from './EditBlockItem.jsx';
import DayHeader from './DayHeader.jsx';

function assignUniqueIds(days) {
  return days.map((day) => ({
    dayNumber: day.dayNumber,
    blocks: day.blocks
      .filter((b) => b.type === 'place' || b.type === 'parking')
      .map((b) => {
        // blockOrder: 블록 자체에 있으면 사용, 없으면 전체 blocks에서 위치 기반 계산
        const blockOrder =
          b.blockOrder ?? day.blocks.findIndex((orig) => orig === b) + 1;
        return {
          ...b,
          blockOrder,
          // courseStore.deleteBlocks가 기대하는 형식
          // place: place-{placeId}-{dayNumber}
          // parking: parking-{name}-{dayNumber}-{blockOrder}
          _uid:
            b.type === 'place'
              ? `place-${b.placeId}-${day.dayNumber}`
              : `parking-${b.name}-${day.dayNumber}-${blockOrder}`,
        };
      }),
  }));
}

function findBlock(localDays, uid) {
  for (const day of localDays) {
    const idx = day.blocks.findIndex((b) => b._uid === uid);
    if (idx !== -1) return { dayNumber: day.dayNumber, idx };
  }
  return null;
}

function moveBlock(localDays, activeId, overId) {
  const activeInfo = findBlock(localDays, activeId);
  const overInfo = findBlock(localDays, overId);
  if (!activeInfo || !overInfo || activeId === overId) return localDays;

  const newLocalDays = localDays.map((day) => ({
    ...day,
    blocks: [...day.blocks],
  }));

  const activeDayIdx = newLocalDays.findIndex(
    (d) => d.dayNumber === activeInfo.dayNumber
  );
  const overDayIdx = newLocalDays.findIndex(
    (d) => d.dayNumber === overInfo.dayNumber
  );

  const isSameDay = activeInfo.dayNumber === overInfo.dayNumber;
  const movingDown = isSameDay && activeInfo.idx < overInfo.idx;

  // 드래그 블록 꺼내기
  const [movedBlock] = newLocalDays[activeDayIdx].blocks.splice(
    activeInfo.idx,
    1
  );

  // 꺼낸 후 over 위치 재계산
  const overBlockIdx = newLocalDays[overDayIdx].blocks.findIndex(
    (b) => b._uid === overId
  );

  // 아래로 이동 시 over 다음에 삽입, 위로 이동 시 over 위치에 삽입
  const insertIdx =
    overBlockIdx === -1
      ? newLocalDays[overDayIdx].blocks.length
      : movingDown
        ? overBlockIdx + 1
        : overBlockIdx;

  newLocalDays[overDayIdx].blocks.splice(insertIdx, 0, movedBlock);

  return newLocalDays;
}

export default function EditBlockList({
  course,
  selectedDay,
  onDaySelect,
  checkedBlocks,
  onCheck,
  onDragEnd,
  onDragMove,
}) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    })
  );

  const [localDays, setLocalDays] = useState(() =>
    assignUniqueIds(course.days)
  );
  const [activeId, setActiveId] = useState(null);

  // store의 course가 바뀌면 (삭제 등) localDays 동기화
  useEffect(() => {
    setLocalDays(assignUniqueIds(course.days));
  }, [course]);

  const activeBlock = activeId ? findBlock(localDays, activeId) : null;
  const activeBlockData = activeBlock
    ? localDays.find((d) => d.dayNumber === activeBlock.dayNumber)?.blocks[
        activeBlock.idx
      ]
    : null;

  const allUniqueIds = localDays.flatMap((day) =>
    day.blocks.map((b) => b._uid)
  );

  const handleDragStart = (event) => {
    setActiveId(event.active.id);
  };

  const handleDragOver = (event) => {
    const { active, over } = event;
    if (!active || !over || active.id === over.id) return;
    const moved = moveBlock(localDays, active.id, over.id);
    setLocalDays(moved);
    // setTimeout으로 렌더링 사이클 분리
    setTimeout(() => onDragMove?.(moved), 0);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    setActiveId(null);
    if (!active || !over) return;
    onDragEnd(localDays);
  };

  const handleDragCancel = () => {
    setLocalDays(assignUniqueIds(course.days));
    setActiveId(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={rectIntersection}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <SortableContext
        items={allUniqueIds}
        strategy={verticalListSortingStrategy}
      >
        <div className="flex flex-col gap-8">
          {localDays.map((localDay) => {
            let placeCount = 0;

            return (
              <div key={localDay.dayNumber}>
                <DayHeader
                  day={localDay.dayNumber}
                  showRefresh={false}
                  isSelected={selectedDay === localDay.dayNumber}
                  onClick={() => onDaySelect(localDay.dayNumber)}
                />
                {localDay.blocks.map((block) => {
                  if (block.type === 'place') placeCount++;

                  return (
                    <EditBlockItem
                      key={block._uid}
                      uniqueId={block._uid}
                      block={block}
                      index={block.type === 'place' ? placeCount : null}
                      isChecked={checkedBlocks.includes(block._uid)}
                      onCheck={() => onCheck(block._uid)}
                      isDragging={block._uid === activeId}
                      dayNumber={localDay.dayNumber}
                    />
                  );
                })}
              </div>
            );
          })}
        </div>
      </SortableContext>

      <DragOverlay>
        {activeBlockData ? (
          <EditBlockItem
            uniqueId={activeBlockData._uid}
            block={activeBlockData}
            index={
              activeBlockData.type === 'place'
                ? activeBlockData.placeOrder
                : null
            }
            isChecked={false}
            onCheck={() => {}}
          />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
