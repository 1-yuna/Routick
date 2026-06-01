import CourseItem from './CourseItem.jsx';
import DayHeader from '../DayHeader.jsx';
import { calcPlaceTimes } from '../../../utils/timeUtils.jsx';

// 일반 모드 - day별 코스 리스트 (시간 계산 포함)
export default function CourseList({
  course,
  selectedDay, // 선택된 day (지도 연동)
  onDaySelect,
  onCardClick,
}) {
  return (
    <div className="flex flex-col gap-12">
      {course.map((dayData, dayIndex) => (
        <div key={dayData.day}>
          {/*day 헤더 - 첫 번째 day만 재추천 버튼 표시*/}
          <DayHeader
            day={dayData.day}
            showRefresh={dayIndex === 0}
            isSelected={selectedDay === dayData.day}
            onClick={() => onDaySelect(dayData.day)}
          />

          {/*장소 리스트 - stayTime/transportTime 기반으로 시간 계산*/}
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
