import WalkIcon from '../../../assets/icons/walk.svg?react';
import CarIcon from '../../../assets/icons/car.svg?react';

// 이동 블록 (도보 / 자동차)
// 레이아웃: 빈 원(○) + 세로 점선 + 아이콘 + 텍스트
export default function MoveItem({ mode, minutes }) {
  return (
    <div className="flex gap-3">
      {/* 왼쪽: 빈 원 + 세로선 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div className="w-3 h-3 rounded-full border border-gray2 bg-white flex-shrink-0" />
        <div className="w-[1px] flex-1 border-l border-dashed border-gray2 min-h-[8px]" />
      </div>

      {/* 오른쪽: 아이콘 + 텍스트 */}
      <div className="flex items-center gap-1 text-gray2 py-3">
        {mode === 'walk' ? (
          <WalkIcon className="w-4 h-4" />
        ) : (
          <CarIcon className="w-4 h-4" />
        )}
        <span className="text-12-rg">
          {mode === 'walk' ? '도보' : '자동차'} {minutes}분
        </span>
      </div>
    </div>
  );
}
