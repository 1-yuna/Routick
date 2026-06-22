import WalkIcon from '../../../assets/icons/walk.svg?react';
import CarIcon from '../../../assets/icons/car.svg?react';
import ParkingIcon from '../../../assets/icons/parking.svg?react';

// 이동 정보 렌더링 헬퍼
function TransportRow({ transport }) {
  if (!transport) return null;
  return (
    <div className="flex items-center gap-1 text-gray2">
      {transport.mode === 'walk' ? (
        <WalkIcon className="w-4 h-4" />
      ) : (
        <CarIcon className="w-4 h-4" />
      )}
      <span className="text-10-rg">
        {transport.mode === 'walk' ? '도보' : '자동차'} {transport.minutes}분
      </span>
    </div>
  );
}

// 주차장 카드 렌더링 헬퍼
function ParkingCard({ name, fee }) {
  return (
    <div className="flex gap-3 bg-neutral rounded-5 p-2">
      <ParkingIcon className="w-5 h-5 text-gray2" />
      <div className="flex flex-col">
        <p className="text-12-sb text-black1">{name}</p>
        {fee && <p className="text-10-rg text-gray2">{fee}</p>}
      </div>
    </div>
  );
}

// 연속된 주차장 블록 그룹
// parkings 배열의 첫 번째 parking의 enterTransport부터
// 마지막 parking의 exitTransport까지 하나의 타임라인으로 표현
export default function ParkingGroupItem({ parkings }) {
  return (
    <div className="flex gap-3">
      {/* 왼쪽: 작은 원 + 세로선 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div className="w-2 h-2 rounded-full bg-parking flex-shrink-0" />
        <div className="w-[1px] flex-1 border-l-2 border-dashed border-gray1" />
      </div>

      {/* 오른쪽: 주차장들 순서대로 */}
      <div className="flex flex-col flex-1 gap-2 pb-3">
        {parkings.map((parking, idx) => (
          <div key={idx} className="flex flex-col gap-2">
            {/* 첫 번째 parking만 enterTransport 표시 */}
            {idx === 0 && <TransportRow transport={parking.enterTransport} />}

            <ParkingCard name={parking.name} fee={parking.fee} />

            {/* parking 사이 이동 (마지막 parking 제외) */}
            {idx < parkings.length - 1 && (
              <TransportRow transport={parking.exitTransport} />
            )}

            {/* 마지막 parking의 exitTransport */}
            {idx === parkings.length - 1 && (
              <TransportRow transport={parking.exitTransport} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
