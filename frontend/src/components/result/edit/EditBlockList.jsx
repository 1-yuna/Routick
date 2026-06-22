import { useState, useEffect } from 'react';
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
  arrayMove,
} from '@dnd-kit/sortable';
import EditBlockItem from './EditBlockItem.jsx';
import DayHeader from '../DayHeader.jsx';

// day별 로컬 블록 상태 관리 컴포넌트
function DayBlockList({
  dayData,
  selectedDay,
  onDaySelect,
  checkedBlocks,
  onCheck,
  onDragEnd,
  sensors,
}) {
  // visible 블록(place/parking)을 로컬 상태로 관리
  const [localBlocks, setLocalBlocks] = useState(
    dayData.blocks.filter((b) => b.type === 'place' || b.type === 'parking')
  );

  // course store가 바뀌면 동기화
  useEffect(() => {
    setLocalBlocks(
      dayData.blocks.filter((b) => b.type === 'place' || b.type === 'parking')
    );
  }, [dayData.blocks]);

  const uniqueIds = localBlocks.map(
    (b) => `${dayData.dayNumber}-${b.blockOrder}`
  );

  let placeCount = 0;

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!active || !over || active.id === over.id) return;

    const activeIdx = localBlocks.findIndex(
      (b) => `${dayData.dayNumber}-${b.blockOrder}` === active.id
    );
    const overIdx = localBlocks.findIndex(
      (b) => `${dayData.dayNumber}-${b.blockOrder}` === over.id
    );

    if (activeIdx === -1 || overIdx === -1) return;

    // 로컬 상태 먼저 업데이트 (애니메이션 자연스럽게)
    const reordered = arrayMove(localBlocks, activeIdx, overIdx);
    setLocalBlocks(reordered);

    // store 업데이트
    onDragEnd(event, dayData.dayNumber, reordered);
  };

  return (
    <div>
      <DayHeader
        day={dayData.dayNumber}
        showRefresh={false}
        isSelected={selectedDay === dayData.dayNumber}
        onClick={() => onDaySelect(dayData.dayNumber)}
      />

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={uniqueIds}
          strategy={verticalListSortingStrategy}
        >
          {localBlocks.map((block) => {
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
      </DndContext>
    </div>
  );
}

// 편집 모드 - 전체 블록 리스트
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
    <div className="flex flex-col gap-8">
      {course.days.map((dayData) => (
        <DayBlockList
          key={dayData.dayNumber}
          dayData={dayData}
          selectedDay={selectedDay}
          onDaySelect={onDaySelect}
          checkedBlocks={checkedBlocks}
          onCheck={onCheck}
          onDragEnd={onDragEnd}
          sensors={sensors}
        />
      ))}
    </div>
  );
}
