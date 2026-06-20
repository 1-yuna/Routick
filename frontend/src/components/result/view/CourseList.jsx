import DayHeader from '../DayHeader.jsx';
import CourseItem from './CourseItem.jsx';
import MoveItem from './MoveItem.jsx';
import ParkingItem from './ParkingItem.jsx';
import ParkingGroupItem from './ParkingGroupItem.jsx';

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

function renderBlocks(blocks, onCardClick) {
  const grouped = groupBlocks(blocks);

  return grouped.map((item) => {
    // 단일 parking
    if (item.type === 'parking') {
      return <ParkingItem key={item.blockOrder} block={item} />;
    }

    // 그룹 parking
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
        return (
          <MoveItem key={item.blockOrder} mode="walk" minutes={item.minutes} />
        );
      default:
        return null;
    }
  });
}

export default function CourseList({
  course,
  selectedDay,
  onDaySelect,
  onCardClick,
}) {
  return (
    <div className="flex flex-col gap-8">
      {course.days.map((dayData, dayIndex) => (
        <div key={dayData.dayNumber}>
          <DayHeader
            day={dayData.dayNumber}
            showRefresh={dayIndex === 0}
            isSelected={selectedDay === dayData.dayNumber}
            onClick={() => onDaySelect(dayData.dayNumber)}
          />
          <div className="pt-4">
            {renderBlocks(dayData.blocks, onCardClick)}
          </div>
        </div>
      ))}
    </div>
  );
}
