import WalkIcon from '../../../assets/icons/walk.svg?react';
import CarIcon from '../../../assets/icons/car.svg?react';

// mode별 아이콘/라벨
// *(v3)* taxi 추가 — 아이콘은 자동차 모양(CarIcon) 재사용, 라벨만 "택시"로 구분
const MODE_CONFIG = {
  walk: { Icon: WalkIcon, label: '도보' },
  car: { Icon: CarIcon, label: '자동차' },
  taxi: { Icon: CarIcon, label: '택시' },
};

// 이동 블록 (도보 / 자동차 / 택시)
// 레이아웃: 빈 원(○) + 세로 점선 + 아이콘 + 텍스트
export default function MoveItem({ mode, minutes }) {
  const { Icon, label } = MODE_CONFIG[mode] ?? MODE_CONFIG.walk;

  return (
    <div className="flex gap-3">
      {/* 왼쪽: 빈 원 + 세로선 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div className="w-2 h-2 rounded-full border border-gray2 bg-white flex-shrink-0" />
        <div className="w-[1px] flex-1 border-l-2 border-dashed border-gray1 min-h-[40px]" />
      </div>

      {/* 오른쪽: 아이콘 + 텍스트 */}
      <div className="flex items-center gap-1 text-gray2 py-5">
        <Icon className="w-4 h-4" />
        <span className="text-10-rg">
          {label} {minutes}분
        </span>
      </div>
    </div>
  );
}
