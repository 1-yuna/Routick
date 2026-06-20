import PlaceImageDefault from '../../../common/imageDefault/PlaceImageDefault.jsx';

const STATUS_COLOR = {
  '영업 중': 'text-green',
  '브레이크 타임': 'text-parking',
  휴무: 'text-red',
};

export default function CourseItem({ block, onCardClick }) {
  const dotColor = block.bucket === 'food' ? 'bg-parking' : 'bg-primary';

  return (
    <div className="flex gap-3">
      {/* 왼쪽: dot + 세로선 (항상 표시) */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${dotColor}`}
        >
          <span className="text-10-sb text-white">{block.placeOrder}</span>
        </div>
        <div className="w-[1px] flex-1 border-l border-dashed border-gray2 min-h-[8px]" />
      </div>

      {/* 오른쪽: 시간 + 카드 */}
      <div className="flex flex-col gap-2 flex-1 pb-3">
        <span className="text-12-rg text-gray2 pt-[2px]">
          {block.arriveTime} ~ {block.leaveTime}
        </span>
        <div
          className="flex gap-3 bg-white rounded-10 shadow-sm p-3 cursor-pointer"
          onClick={onCardClick}
        >
          {block.src ? (
            <img
              src={block.src}
              alt={block.name}
              className="w-20 h-20 rounded-5 object-cover flex-shrink-0"
            />
          ) : (
            <PlaceImageDefault className="w-20 h-20 rounded-5 flex-shrink-0" />
          )}
          <div className="flex flex-col gap-1 justify-center">
            <p className="text-14-sb text-black1">{block.name}</p>
            {block.status && (
              <p
                className={`text-12-rg ${STATUS_COLOR[block.status] ?? 'text-gray2'}`}
              >
                ● {block.status}
              </p>
            )}
            <p className="text-10-rg text-gray2 line-clamp-2">
              {block.description}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
