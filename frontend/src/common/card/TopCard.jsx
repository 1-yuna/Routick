// 홈 - Top5 추천 카드 (이미지 + 해시태그)
export default function TopCard({ image, tags = [], onClick }) {
  return (
    <button
      onClick={onClick}
      className="relative flex-shrink-0 w-[150px] h-[180px] rounded-xl overflow-hidden shadow-xl"
    >
      {/*배경 이미지*/}
      <img className="h-full w-full object-cover" src={image} alt="card" />

      {/*어두운 오버레이*/}
      <div className="absolute inset-0 bg-black/35"></div>

      {/*해시태그*/}
      <div className="absolute flex flex-col items-start bottom-2 left-3 text-white text-12-sb">
        {tags.map((tag, index) => (
          <p key={index}>#{tag}</p>
        ))}
      </div>
    </button>
  );
}
