// 홈 - 놀거리 섹션 카드 (핫플/전시/자연)
export default function PlayCard({ icon, text, onClick }) {
  return (
    <button
      onClick={onClick}
      className=" flex flex-col items-center justify-center w-[88px] h-[92px] rounded-5 bg-white shadow-sm"
    >
      <p className="text-24-sb">{icon}</p>
      <p className="text-black1 text-12-sb">{text}</p>
    </button>
  );
}
