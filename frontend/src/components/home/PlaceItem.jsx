import PlaceImageDefault from '../../common/imageDefault/PlaceImageDefault.jsx';

// 놀거리 추천 페이지 - 장소 리스트 아이템 (이미지 + 순위 번호 + 정보)
// 1~3위는 bg-label, 4위 이하는 bg-gray2
export default function PlaceItem({ place, index, onClick }) {
  const { name, longDescription, address, src } = place;

  return (
    <div
      className="flex gap-4 py-4 border-b border-line1 cursor-pointer"
      onClick={onClick}
    >
      {/*이미지 + 순위 번호 - 이미지 없으면 기본 이미지*/}
      <div className="relative flex-shrink-0">
        {src ? (
          <img
            src={src}
            alt={name}
            className="w-28 h-28 rounded-5 object-cover"
          />
        ) : (
          <PlaceImageDefault className="w-28 h-28 rounded-5" />
        )}
        <div
          className={`absolute top-1 left-1 w-5 h-5 rounded-5 flex items-center justify-center ${index <= 3 ? 'bg-label' : 'bg-gray2'}`}
        >
          <span className="text-10-sb text-white">{index}</span>
        </div>
      </div>

      {/*장소 정보*/}
      <div className="flex flex-col justify-between">
        <p className="text-16-sb text-black1">{name}</p>
        <p className="text-12-rg text-black1 line-clamp-3">{longDescription}</p>
        <p className="text-10-sb text-gray2">{address}</p>
      </div>
    </div>
  );
}
