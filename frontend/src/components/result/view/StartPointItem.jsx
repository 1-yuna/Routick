import MapIcon from '../../../assets/icons/map.svg?react';

// 출발지/도착지 블록 - 이름만 표시
// 이동시간은 첫/마지막 블록의 enterTransport/exitTransport가 담당
export default function StartPointItem({ name, isEnd = false }) {
  return (
    <div className="flex gap-3 h-[46px]">
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            isEnd ? 'border border-gray2 bg-white' : 'bg-primary'
          }`}
        />
        {!isEnd && (
          <div className="w-[1px] flex-1 border-l-2 border-dashed border-gray1 min-h-[8px]" />
        )}
      </div>
      <div className="flex h-[10px] items-center gap-1 text-gray2">
        <MapIcon className="flex items-center w-3 h-3" />
        <span className="text-12-rg">{name}</span>
      </div>
    </div>
  );
}
