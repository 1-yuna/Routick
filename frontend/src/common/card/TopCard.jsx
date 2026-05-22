// 홈 - Top5에 들어가는 card
export default function TopCard({ image, tags = [], onClick }) {
  return (
    // card
    <button
      onClick={onClick}
      className="relative flex-shrink-0 w-[150px] h-[180px] rounded-xl overflow-hidden shadow-xl"
    >
      <img className="h-full w-full object-cover" src={image} alt="card" />

      {/* overlay */}
      <div className="absolute inset-0 bg-black/35"></div>

      {/* 텍스트 */}
      <div className="absolute flex flex-col items-start bottom-2 left-3 text-white text-12-sb">
        {tags.map((tag, index) => (
          <p key={index}>#{tag}</p>
        ))}
      </div>
    </button>
  );
}
