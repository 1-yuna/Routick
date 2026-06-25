// 출발지/도착지 블록
// start: 주황 dot(8px) + 아래 점선, 옆에 시간 + 이름
// end:   점선 → 주황 dot(8px) → 짧은 점선 → 주황 dot(8px) + 시간 + 이름
export default function StartPointItem({ name, time, isEnd = false }) {
  return (
    <div className="flex gap-3 h-12">
      {/* 왼쪽: dot + 선 구조 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        {isEnd ? (
          <>
            {/* 첫 번째 dot */}
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
            {/* 점선 */}
            <div className="w-[1px] h-full border-l-2 border-dashed border-gray1" />
            {/* 두 번째 dot */}
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
          </>
        ) : (
          <>
            {/* start dot */}
            <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#FF8A5C]" />
            {/* 아래 점선 */}
            <div className="w-[1px] h-full border-l-2 border-dashed border-gray1" />
          </>
        )}
      </div>

      {/* 오른쪽: 시간 + 이름 - end면 두 번째 dot에 맞게 아래 정렬 */}
      <div className={`flex text-gray2 ${isEnd ? 'items-end' : 'items-start'}`}>
        <div className="flex items-center gap-2">
          {time && <span className="text-12-sb text-black1">{time}</span>}
          <span className="text-12-rg">{name}</span>
        </div>
      </div>
    </div>
  );
}
