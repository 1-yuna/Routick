// 코스 헤더
export default function DayHeader({ day, showRefresh }) {
  return (
    <div className="flex pb-4 justify-between items-center">
      <p className="text-16-sb text-black1">day {day}</p>
      {showRefresh && (
        <button className="text-14-rg text-gray2">새로고침</button>
      )}
    </div>
  );
}
