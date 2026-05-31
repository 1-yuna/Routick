// 코스 헤더
export default function DayHeader({ day, showRefresh, isSelected, onClick }) {
  return (
    <div className="flex py-4 justify-between items-center" onClick={onClick}>
      <p
        className={`text-16-sb ${isSelected ? 'text-primary' : 'text-black1'}`}
      >
        day {day}
      </p>
      {showRefresh && <button className="text-14-rg text-gray2">재추천</button>}
    </div>
  );
}
