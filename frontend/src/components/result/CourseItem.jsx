// components/course/CourseItem.jsx
import StarIcon from '../../assets/icons/star.svg?react';
import CarIcon from '../../assets/icons/car.svg?react';
import WalkIcon from '../../assets/icons/walk.svg?react';

// 결과 페이지 - 코스 list
// components/course/CourseItem.jsx
export default function CourseItem({ place, isLast }) {
  return (
    <div className="flex flex-col">
      {/* a: 시간 + 번호바 + 카드 */}
      <div className="flex gap-3">
        {/* 시간 */}
        <div className="flex flex-col justify-between text-right w-10">
          <span className="text-12-rg text-gray2">{place.time}</span>
          <span className="text-12-rg text-gray2">{place.endTime}</span>
        </div>

        {/* 번호 + 바 */}
        <div className="flex flex-col items-center">
          <div
            className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${place.id <= 3 ? 'bg-label' : 'bg-primary'}`}
          >
            <span className="text-10-sb text-white">{place.id}</span>
          </div>
          <div className="w-[1px] flex-1 border-l border-dashed border-gray2" />
          <div className="w-3 h-3 rounded-full border-2 border-primary flex-shrink-0" />
        </div>

        {/* 카드 */}
        <div className="flex gap-3 bg-white rounded-[10px] shadow-[2px_2px_10px_5px_rgba(0,0,0,0.05)] p-3 mb-3 flex-1">
          <img
            src={place.src}
            alt={place.name}
            className="w-20 h-20 rounded-[8px] object-cover"
          />
          <div className="flex flex-col gap-1 justify-center">
            <p className="text-14-sb text-black1">{place.name}</p>
            <div className="flex items-center gap-[2px]">
              <StarIcon className="w-3 h-3 text-food" />
              <span className="text-10-sb text-black1">{place.rating}</span>
              <span className="text-10-rg text-gray2">
                ({place.reviewCount})
              </span>
            </div>
            <p className="text-10-rg text-gray2">{place.description}</p>
          </div>
        </div>
      </div>

      {/* b: 이동수단 */}
      {!isLast && (
        <div className="flex items-center gap-2 pl-24 py-2">
          {place.transport === '자동차' ? (
            <CarIcon className="w-4 h-4 text-gray2" />
          ) : (
            <WalkIcon className="w-4 h-4 text-gray2" />
          )}
          <span className="text-12-rg text-gray2">
            {place.transport} {place.transportTime}
          </span>
        </div>
      )}
    </div>
  );
}
