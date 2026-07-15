import TopCard from '../../common/card/TopCard.jsx';

export default function TopCardSection({
  name,
  area,
  className = '',
  items = [],
  onClick,
  loading = false,
}) {
  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      <p className="text-black1 text-16-sb">
        {name}님을 위한 {area} 추천
      </p>

      <div className="flex overflow-x-auto gap-5 pr-6 no-scrollbar">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="flex items-center justify-center gap-1.5 w-[120px] h-[160px] rounded-10 bg-neutral shrink-0"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce" />
              </div>
            ))
          : items.map((item, index) => (
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
