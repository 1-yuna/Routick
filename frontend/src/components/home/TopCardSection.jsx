import TopCard from '../../common/card/TopCard.jsx';

// 홈 - 지역 추천 카드 섹션 (가로 스크롤)
export default function TopCardSection({
  name,
  area,
  className = '',
  items = [],
  onClick,
}) {
  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      {/*텍스트*/}
      <p className="text-black1 text-16-sb">
        {name}님을 위한 {area} 추천
      </p>

      {/*가로 스크롤 카드 목록*/}
      <div className="flex overflow-x-auto gap-5 pr-6 no-scrollbar">
        {items.map((item, index) => (
          <TopCard
            key={index}
            image={item.src}
            title={item.name}
            tags={item.tags}
            onClick={onClick ? () => onClick(item) : undefined}
          />
        ))}
      </div>
    </div>
  );
}
