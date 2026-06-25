import { useNavigate } from 'react-router-dom';
import WalkIcon from '../../../assets/icons/walk.svg?react';
import CarIcon from '../../../assets/icons/car.svg?react';
import ParkingIcon from '../../../assets/icons/parking.svg?react';

// 이동수단 아이콘 + 분
function TransportChip({ transport }) {
  if (!transport) return <div />;
  const Icon = transport.mode === 'walk' ? WalkIcon : CarIcon;
  return (
    <div className="flex items-center justify-center gap-1 text-gray2">
      <Icon className="w-3 h-3" />
      <span className="text-10-rg">{transport.minutes}분</span>
    </div>
  );
}

// 주차장 이름 + P 아이콘
function ParkingChip({ name, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center justify-center gap-1 text-gray2 active:opacity-70 overflow-hidden"
    >
      <ParkingIcon className="w-3 h-3 flex-shrink-0" />
      <span className="text-10-rg truncate">{name}</span>
    </button>
  );
}

// 연속된 주차장 블록 그룹
export default function ParkingGroupItem({ parkings }) {
  const navigate = useNavigate();

  const handleParkingClick = (parking) => {
    navigate(`/place/${encodeURIComponent(parking.name)}`, {
      state: {
        name: parking.name,
        lat: parking.lat,
        lng: parking.lng,
        description: parking.description ?? '',
      },
    });
  };

  return (
    <div className="flex gap-3">
      {/* 왼쪽: dot + 세로선 */}
      <div className="flex flex-col items-center flex-shrink-0 w-5">
        <div className="w-2 h-2 rounded-full bg-parking flex-shrink-0" />
        <div className="w-[1px] flex-1 border-l-2 border-dashed border-gray1 min-h-[8px]" />
      </div>

      {/* 오른쪽: 시간 + 주차장별 인라인 정보 */}
      <div className="flex flex-col gap-2 flex-1 pb-5">
        {/* 그룹 시간: 첫 번째 arriveTime ~ 마지막 leaveTime */}
        {parkings[0].arriveTime && parkings[parkings.length - 1].leaveTime && (
          <span className="text-12-sb text-black1">
            {parkings[0].arriveTime} ~ {parkings[parkings.length - 1].leaveTime}
          </span>
        )}

        {parkings.map((parking, idx) => {
          const isLast = idx === parkings.length - 1;
          return (
            <div key={idx} className="flex w-full items-center">
              <div className="flex items-center justify-center w-16">
                <TransportChip transport={parking.enterTransport} />
              </div>
              <div className="flex items-center justify-center flex-1 px-3 border-x border-line2">
                <ParkingChip
                  name={parking.name}
                  onClick={() => handleParkingClick(parking)}
                />
              </div>
              <div className="flex items-center justify-center w-16">
                {isLast && <TransportChip transport={parking.exitTransport} />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
