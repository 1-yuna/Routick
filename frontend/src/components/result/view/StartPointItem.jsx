// 출발지/도착지 블록
// start: 주황 dot(8px) + 아래 점선, 옆에 시간 + 이름
// end:   점선 → 주황 dot(8px) → 짧은 점선 → 주황 dot(8px) + 시간 + 이름
export default function StartPointItem({ name, time, isEnd = false, onClick }) {
  return (
    <div className="flex gap-3 h-12">
      {/* 왼쪽: dot + 선 구조 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        {isEnd ? (
          <>
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
            <div className="w-[1px] h-full border-l-2 border-dashed border-gray1" />
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
          </>
        ) : (
          <>
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
            <div className="w-[1px] h-full border-l-2 border-dashed border-gray1" />
          </>
        )}
      </div>

      {/* 오른쪽: 시간 + 이름 */}
      <div
        className={`flex text-gray2 cursor-pointer active:opacity-70 ${isEnd ? 'items-end' : 'items-start'}`}
        onClick={onClick}
      >
        <div className="flex items-center gap-2">
          {time && <span className="text-12-sb text-black1">{time}</span>}
          <span className="text-12-rg">{name}</span>
        </div>
      </div>
    </div>
  );
}
