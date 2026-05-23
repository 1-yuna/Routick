import StarIcon from '../../assets/icons/star.svg?react';
import PlaceImageDefault from '../../common/default/PlaceImageDefault.jsx';

// 상세보기 - 하단 카드
export default function PlaceCard({
  name,
  rating,
  reviewCount,
  description,
  src,
}) {
  return (
    <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-10 bg-white rounded-[10px] p-5 w-[327px] h-[148px] shadow-[2px_2px_10px_5px_rgba(0,0,0,0.1)]">
      <div className="flex gap-4">
        {/*이미지*/}
        {src ? (
          <img
            src={src}
            alt="장소 이미지"
            className="w-28 h-28 object-cover rounded-lg"
          />
        ) : (
          <PlaceImageDefault className="w-28 h-28 rounded-lg" />
        )}
        {/*정보*/}
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <p className="text-16-sb text-black1">{name}</p>
            <div className="flex items-center gap-[2px]">
              <StarIcon className="w-3 h-3 text-food" />
              <span className="text-10-sb text-black1">{rating}</span>
              <span className="text-10-rg text-gray2">({reviewCount})</span>
            </div>
          </div>
          <p className="w-36 text-10-rg text-gray2">{description}</p>
          <button className="grid place-items-center w-24 h-6 bg-primary rounded-[2px] text-white text-12-rg">
            바로가기
          </button>
        </div>
      </div>
    </div>
  );
}
