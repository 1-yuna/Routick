// 결과 페이지 - day 헤더 (선택된 day는 primary 색상, 첫 번째 day만 재추천 버튼 표시)
export default function DayHeader({ day, showRefresh, isSelected, onClick }) {
  return (
    <div className="flex py-4 justify-between items-center" onClick={onClick}>
      {/*선택된 day면 primary 색상*/}
      <p
        className={`text-16-sb ${isSelected ? 'text-primary' : 'text-black1'}`}
      >
        day {day}
      </p>
      {/*첫 번째 day에만 재추천 버튼 표시*/}
      {showRefresh && <button className="text-14-rg text-gray2">재추천</button>}
    </div>
  );
}
