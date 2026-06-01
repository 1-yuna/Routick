import StarIcon from '../../assets/icons/star.svg?react';
import CarIcon from '../../assets/icons/car.svg?react';
import WalkIcon from '../../assets/icons/walk.svg?react';

// 결과 페이지 - 코스 리스트 아이템 (시간 + 타임라인 + 장소 카드 + 이동수단)
export default function CourseItem({ place, isLast, onCardClick, index }) {
  // 너비
  const TIME_WIDTH = 'w-8';
  const DOT_WIDTH = 'w-5';

  // 카테고리별 마커 색상
  const CATEGORY_COLOR = {
    food: 'bg-food',
    lodging: 'bg-lodging',
  };
  const CATEGORY_BORDER = {
    food: 'border-food',
    lodging: 'border-lodging',
  };

  return (
    <div className="flex flex-col">
      {/*시간 + 타임라인 + 장소 카드*/}
      <div className="flex gap-3">
        {/*시작/종료 시간*/}
        <div
          className={`flex flex-col justify-between text-left ${TIME_WIDTH}`}
        >
          <span className="text-12-rg text-gray2">{place.time}</span>
          <span className="text-12-rg text-gray2">{place.endTime}</span>
        </div>

        {/* 번호 + 바 */}
        <div className="flex flex-col items-center">
          <div
            className={`${DOT_WIDTH} h-5 rounded-full flex items-center justify-center flex-shrink-0 ${CATEGORY_COLOR[place.category] || 'bg-primary'}`}
          >
            <span className="text-10-sb text-white">{index + 1}</span>
          </div>
          <div className="w-[1px] flex-1 border-l border-dashed border-gray2" />
          <div
            className={`w-3 h-3 rounded-full border-2 flex-shrink-0 ${CATEGORY_BORDER[place.category] || 'border-primary'}`}
          />
        </div>

        {/*장소 카드*/}
        <div
          className="flex gap-2 bg-white rounded-[10px] shadow-[2px_2px_10px_5px_rgba(0,0,0,0.05)] p-3 flex-1"
          onClick={onCardClick}
        >
          {/*사진*/}
          <img
            src={place.src}
            alt={place.name}
            className="w-20 h-20 rounded-[8px] object-cover flex-shrink-0"
          />
          {/*장소 정보*/}
          <div className="flex flex-col justify-between">
            <div className="flex flex-col gap-1">
              <p className="text-14-sb text-black1">{place.name}</p>
              <div className="flex items-center gap-[2px]">
                <StarIcon className="w-3 h-3 text-food" />
                <span className="text-10-sb text-black1">{place.rating}</span>
                <span className="text-10-rg text-gray2">
                  ({place.reviewCount})
                </span>
              </div>
            </div>

            <p className="text-10-rg text-gray2">{place.description}</p>
          </div>
        </div>
      </div>

      {/*이동수단 - 마지막 장소면 표시 안 함*/}
      {!isLast && (
        <div className="flex gap-3">
          {/*시간 자리 빈 공간*/}
          <div className={TIME_WIDTH} />

          {/* 선 */}
          <div className={`flex flex-col ${DOT_WIDTH} items-center`}>
            <div className="w-[1px] flex-1 border-l border-dashed border-gray2" />
          </div>

          {/*이동수단 아이콘 + 텍스트 - transport 없으면 표시 안 함*/}
          <div className="flex items-center gap-2 py-4">
            {place.transport && (
              <div className="flex items-center gap-2 py-4">
                {place.transport === '자동차' ? (
                  <CarIcon className="w-4 h-4 text-gray2" />
                ) : (
                  <WalkIcon className="w-4 h-4 text-gray2" />
                )}
                <span className="text-12-rg text-gray2">
                  {place.transport} {place.transportTime}분
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
