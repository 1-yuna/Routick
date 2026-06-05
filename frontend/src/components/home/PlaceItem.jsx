import StarIcon from '../../assets/icons/star.svg?react';

// 놀거리 추천 페이지 - 장소 리스트 아이템 (이미지 + 순위 번호 + 정보)
// 1~3위는 bg-label, 4위 이하는 bg-gray2
export default function PlaceItem({ place, index, onClick }) {
  const { name, rating, reviewCount, address, src } = place;

  return (
    <div className="flex gap-4 cursor-pointer" onClick={onClick}>
      {/*이미지 + 순위 번호*/}
      <div className="relative flex-shrink-0">
        <img
          src={src}
          alt={name}
          className="w-22 h-24 rounded-[10px] object-cover"
        />
        <div
          className={`absolute top-1 left-1 w-5 h-5 rounded-[5px] flex items-center justify-center ${index <= 3 ? 'bg-label' : 'bg-gray2'}`}
        >
          <span className="text-10-sb text-white">{index}</span>
        </div>
      </div>

      {/*장소 정보*/}
      <div className="flex flex-col py-1 justify-between">
        <div className="flex flex-col">
          <p className="text-16-sb text-black1">{name}</p>
          <div className="flex items-center gap-[2px]">
            <StarIcon className="w-3 h-3 text-food" />
            <span className="text-10-sb text-black1">{rating}</span>
            <span className="text-10-rg text-gray2">({reviewCount})</span>
          </div>
        </div>
        <p className="text-10-sb text-gray2">{address}</p>
      </div>
    </div>
  );
}
