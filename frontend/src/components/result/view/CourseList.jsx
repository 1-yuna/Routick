// components/result/CourseList.jsx
import CourseItem from './CourseItem.jsx';
import DayHeader from '../DayHeader.jsx';
import { calcPlaceTimes } from '../../../utils/timeUtils.jsx';

// 일반 모드 - 코스 리스트
export default function CourseList({
  course,
  selectedDay,
  onDaySelect,
  onCardClick,
}) {
  return (
    <div className="flex flex-col gap-12">
      {course.map((dayData, dayIndex) => (
        <div key={dayData.day}>
          <DayHeader
            day={dayData.day}
            showRefresh={dayIndex === 0}
            isSelected={selectedDay === dayData.day}
            onClick={() => onDaySelect(dayData.day)}
          />
          <div>
            {calcPlaceTimes(dayData.places).map((place, index) => (
              <CourseItem
                key={index}
                index={index}
                place={place}
                transport={dayData.transport}
                isLast={index === dayData.places.length - 1}
                onCardClick={() => onCardClick(place)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
