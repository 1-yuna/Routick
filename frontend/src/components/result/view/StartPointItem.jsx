import Map2Icon from '../../../assets/icons/map2.svg?react';

// 출발지/도착지 블록 - 뱃지 스타일
// 핀 아이콘 + 출발/도착 라벨 + 장소명 + 시간
export default function StartPointItem({ name, isEnd = false, onClick }) {
  return (
    <button
      type="button"
      className={`w-full flex items-center gap-3 bg-mark/5 rounded-5 px-3 py-2 ${isEnd ? 'mt-[28px]' : 'mb-[28px]'}`}
      onClick={onClick}
    >
      <div className="flex items-center gap-2">
        {/* 핀 아이콘 */}
        <Map2Icon className="w-4 h-4 text-mark" />

        {/* 출발/도착 라벨 */}
        <span className="text-12-sb text-mark flex-shrink-0">
          {isEnd ? '도착' : '출발'}
        </span>
      </div>

      {/* 장소명 */}
      <span className="text-12-sb text-black1 flex-1 flex items-start">
        {name}
      </span>
    </button>
  );
}
