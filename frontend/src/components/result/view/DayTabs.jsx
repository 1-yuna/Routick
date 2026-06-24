// 결과 페이지 - Day 탭 (pill 버튼 스타일)
// 선택된 day는 primary 배경 + 흰 텍스트, 비선택은 border + gray 텍스트
export default function DayTabs({ days, selectedDay, onDaySelect, onRefresh }) {
  return (
    <div className="flex items-center justify-between">
      {/* Day 탭들 */}
      <div className="flex gap-2">
        {days.map((day) => {
          const isSelected = selectedDay === day;
          return (
            <button
              key={day}
              onClick={() => onDaySelect(day)}
              className={`flex justify-center items-center w-16 h-8 rounded-full text-12-sb ${
                isSelected
                  ? 'bg-primary text-white'
                  : 'bg-white border border-line2 text-gray2'
              }`}
            >
              Day {day}
            </button>
          );
        })}
      </div>

      {/* 재추천 버튼 */}
      <button className="text-14-rg text-gray2" onClick={onRefresh}>
        재추천
      </button>
    </div>
  );
}
