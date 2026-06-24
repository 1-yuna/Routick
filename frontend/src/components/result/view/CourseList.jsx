import DayTabs from './DayTabs.jsx';
import CourseItem from './CourseItem.jsx';
import MoveItem from './MoveItem.jsx';
import ParkingGroupItem from './ParkingGroupItem.jsx';
import StartPointItem from './StartPointItem.jsx';

// 연속된 parking 블록을 그룹핑하여 렌더링 단위로 변환
function groupBlocks(blocks) {
  const result = [];
  let i = 0;

  while (i < blocks.length) {
    const block = blocks[i];

    if (block.type === 'parking') {
      const group = [block];
      while (i + 1 < blocks.length && blocks[i + 1].type === 'parking') {
        i++;
        group.push(blocks[i]);
      }
      result.push({
        type: 'parkingGroup',
        parkings: group,
        key: block.blockOrder,
      });
    } else {
      result.push(block);
    }
    i++;
  }

  return result;
}

function renderBlocks(blocks, onCardClick, hasEnd = false) {
  const grouped = groupBlocks(blocks);

  return (
    <>
      {grouped.map((item) => {
        if (item.type === 'parkingGroup') {
          return <ParkingGroupItem key={item.key} parkings={item.parkings} />;
        }

        switch (item.type) {
          case 'place':
            return (
              <CourseItem
                key={item.blockOrder}
                block={item}
                onCardClick={() => onCardClick(item)}
              />
            );
          case 'walk':
            // mode가 있으면 mode 사용, 없으면 기본 'walk'
            return (
              <MoveItem
                key={item.blockOrder}
                mode={item.mode ?? 'walk'}
                minutes={item.minutes}
              />
            );
          default:
            return null;
        }
      })}

      {/* 마지막 종료 표시 원 - end 없을 때만 */}
      {!hasEnd && (
        <div className="flex items-center gap-3">
          <div className="w-5 flex justify-center flex-shrink-0">
            <div className="w-2 h-2 rounded-full border border-gray2 bg-white" />
          </div>
        </div>
      )}
    </>
  );
}

export default function CourseList({
  course,
  selectedDay,
  onDaySelect,
  onCardClick,
}) {
  const dayNumbers = course.days.map((d) => d.dayNumber);
  const selectedDayData = course.days.find((d) => d.dayNumber === selectedDay);

  return (
    <div className="flex flex-col gap-6">
      <DayTabs
        days={dayNumbers}
        selectedDay={selectedDay}
        onDaySelect={onDaySelect}
      />
      {selectedDayData && (
        <div>
          {selectedDayData.start && (
            <StartPointItem name={selectedDayData.start.name} />
          )}
          {renderBlocks(
            selectedDayData.blocks,
            onCardClick,
            !!selectedDayData.end
          )}
          {selectedDayData.end && (
            <>
              {selectedDayData.end.enterTransport && (
                <MoveItem
                  mode={selectedDayData.end.enterTransport.mode}
                  minutes={selectedDayData.end.enterTransport.minutes}
                />
              )}
              <StartPointItem name={selectedDayData.end.name} isEnd />
            </>
          )}
        </div>
      )}
    </div>
  );
}
