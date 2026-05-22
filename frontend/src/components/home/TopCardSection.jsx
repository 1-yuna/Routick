import TopCard from '../../common/card/TopCard.jsx';

// Top5 카드
export default function TopCardSection({
  name,
  className = '',
  items = [],
  onClick,
}) {
  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      {/*텍스트*/}
      <p className="text-black1 text-16-sb">{name}님을 위한 먹거리 TOP5</p>

      {/*이미지*/}
      <div className="flex overflow-x-auto gap-5 no-scrollbar">
        {items.map((item, index) => (
          <TopCard
            key={index}
            image={item.image}
            tags={item.tags}
            onClick={onClick}
          />
        ))}
      </div>
    </div>
  );
}
