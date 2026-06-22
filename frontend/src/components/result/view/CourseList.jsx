import DayHeader from '../DayHeader.jsx';
import CourseItem from './CourseItem.jsx';
import MoveItem from './MoveItem.jsx';
import ParkingGroupItem from './ParkingGroupItem.jsx';

// 연속된 parking 블록을 그룹핑하여 렌더링 단위로 변환
// [place, walk, place, parking, parking, place]
// → [place, walk, place, parkingGroup([p,p]), place]
// 단일 parking도 parkingGroup으로 묶임 (ParkingGroupItem이 1개/다수 모두 처리)
function groupBlocks(blocks) {
  const result = [];
  let i = 0;

  while (i < blocks.length) {
    const block = blocks[i];

    if (block.type === 'parking') {
      // 연속된 parking 블록 모으기
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

// 그룹핑된 블록 배열을 순서대로 렌더링
function renderBlocks(blocks, onCardClick) {
  const grouped = groupBlocks(blocks);

  return grouped.map((item) => {
    // 주차장 그룹 (단일/다수 모두 ParkingGroupItem으로 처리)
    if (item.type === 'parkingGroup') {
      return <ParkingGroupItem key={item.key} parkings={item.parkings} />;
    }

    switch (item.type) {
      // 장소 블록
      case 'place':
        return (
          <CourseItem
            key={item.blockOrder}
            block={item}
            onCardClick={() => onCardClick(item)}
          />
        );
      // 도보 이동 블록
      case 'walk':
        return (
          <MoveItem key={item.blockOrder} mode="walk" minutes={item.minutes} />
        );
      default:
        return null;
    }
  });
}

// 결과 페이지 - 코스 타임라인 리스트
// day 탭 선택 시 해당 day의 blocks를 렌더링
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
          {/* day 헤더 (Day 1, Day 2 ...) */}
          <DayHeader
            day={dayData.dayNumber}
            showRefresh={dayIndex === 0}
            isSelected={selectedDay === dayData.dayNumber}
            onClick={() => onDaySelect(dayData.dayNumber)}
          />
          {/* 타임라인 블록 렌더링 */}
          <div className="pt-4">
            {renderBlocks(dayData.blocks, onCardClick)}
          </div>
        </div>
      ))}
    </div>
  );
}
