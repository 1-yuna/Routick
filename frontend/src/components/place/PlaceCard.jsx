import PlaceImageDefault from '../../common/imageDefault/PlaceImageDefault.jsx';

// 장소 상세보기 - 하단 카드 (이미지, 이름, 설명, 카카오맵 바로가기)
export default function PlaceCard({ place }) {
  const { name, description, src, placeId } = place;

  return (
    <div className="absolute bottom-[88px] left-1/2 -translate-x-1/2 z-10 bg-white rounded-5 p-4 w-[327px] h-[128px] shadow-lg">
      <div className="flex gap-4">
        {/*이미지 - 없으면 기본 이미지*/}
        {src ? (
          <img
            src={src}
            alt="장소 이미지"
            className="w-24 h-24 object-cover rounded-5"
          />
        ) : (
          <PlaceImageDefault className="w-24 h-24 rounded-5" />
        )}

        {/*장소 정보*/}
        <div className="flex flex-col justify-between">
          <div className="flex flex-col gap-1">
            <p className="text-16-sb text-black1">{name}</p>
            <p className="w-36 text-10-rg text-gray2">{description}</p>
          </div>

          {/*카카오맵 새 탭으로 열기 - placeId 있을 때만*/}
          {placeId && (
            <button
              onClick={() =>
                window.open(`https://place.map.kakao.com/${placeId}`, '_blank')
              }
              className="grid place-items-center w-[92px] h-6 bg-primary rounded-2 text-white text-12-rg"
            >
              바로가기
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
