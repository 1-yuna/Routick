import WalkIcon from '../../../assets/icons/walk.svg?react';
import CarIcon from '../../../assets/icons/car.svg?react';

// 주차장 블록
// 레이아웃: 작은 원(○) → enterTransport → [P] 카드 → exitTransport
export default function ParkingItem({ block }) {
  const { enterTransport, exitTransport, name, fee } = block;

  return (
    <div className="flex gap-3">
      {/* 왼쪽: 작은 원 + 세로선 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div className="w-3 h-3 rounded-full border border-gray2 bg-white flex-shrink-0" />
        <div className="w-[1px] flex-1 border-l border-dashed border-gray2" />
      </div>

      {/* 오른쪽: enterTransport + 카드 + exitTransport */}
      <div className="flex flex-col gap-2 flex-1 py-1">
        {/* enterTransport */}
        {enterTransport && (
          <div className="flex items-center gap-1 text-gray2">
            {enterTransport.mode === 'walk' ? (
              <WalkIcon className="w-4 h-4" />
            ) : (
              <CarIcon className="w-4 h-4" />
            )}
            <span className="text-12-rg">
              {enterTransport.mode === 'walk' ? '도보' : '자동차'}{' '}
              {enterTransport.minutes}분
            </span>
          </div>
        )}

        {/* 주차장 카드 */}
        <div className="flex items-center gap-3 bg-white rounded-10 shadow-sm px-4 py-3">
          <div className="w-9 h-9 rounded-5 border border-gray2 flex items-center justify-center flex-shrink-0">
            <span className="text-14-sb text-gray2">P</span>
          </div>
          <div className="flex flex-col">
            <p className="text-14-sb text-black1">{name}</p>
            {fee && <p className="text-12-rg text-gray2">{fee}</p>}
          </div>
        </div>

        {/* exitTransport */}
        {exitTransport && (
          <div className="flex items-center gap-1 text-gray2 pb-2">
            {exitTransport.mode === 'walk' ? (
              <WalkIcon className="w-4 h-4" />
            ) : (
              <CarIcon className="w-4 h-4" />
            )}
            <span className="text-12-rg">
              {exitTransport.mode === 'walk' ? '도보' : '자동차'}{' '}
              {exitTransport.minutes}분
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
