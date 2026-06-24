import MapIcon from '../../assets/icons/map.svg?react';
import CarIcon from '../../assets/icons/car.svg?react';
import WalkIcon from '../../assets/icons/walk.svg?react';

// 여행 카드
export default function TripCard({ trip, onClick }) {
  const { title, region, transport, tags, hashtags, src } = trip;

  return (
    <div
      className="flex w-full h-[115px] bg-white rounded-10 shadow-md cursor-pointer"
      onClick={onClick}
    >
      {/*이미지*/}
      <div className="relative flex-shrink-0">
        <img
          src={src}
          alt={title}
          className="w-[104px] h-full rounded-l-10 object-cover"
        />

        {/*어두운 오버레이*/}
        <div className="absolute inset-0 bg-black/45 rounded-l-10" />

        {/*주소*/}
        <div className="absolute top-2 left-2 flex items-center text-white gap-1">
          <MapIcon className="w-3 h-3" />
          <span className="text-10-rg">{region}</span>
        </div>

        {/*해시태그*/}
        <div className="absolute bottom-2 left-2 flex flex-col">
          {hashtags.map((tag) => (
            <span key={tag} className="text-10-rg text-white">
              #{tag}
            </span>
          ))}
        </div>
      </div>

      {/*정보*/}
      <div className="flex flex-col p-3 gap-2 flex-1">
        {/*이동수단 + 제목*/}
        <div className="flex items-center gap-1">
          {transport === '도보' ? (
            <WalkIcon className="w-5 h-5 text-black1" />
          ) : (
            <CarIcon className="w-5 h-5 text-black1" />
          )}
          <p className="text-12-sb text-black1">{title}</p>
        </div>

        {/*태그*/}
        <div className="flex flex-wrap gap-1">
          {tags.map((tag) => (
            <span
              key={tag}
              className="px-[15px] py-[2px] rounded-[2px] bg-login border border-line1 text-10-rg text-primary"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
