// 홈 - 놀거리에 들어가는 card
export default function TopCard({ icon, text, onClick }) {
  return (
    // card
    <button
      onClick={onClick}
      className=" flex flex-col items-center justify-center w-[88px] h-[92px] rounded-xl bg-white shadow-[0px_2px_4px_rgba(0,0,0,0.25)]"
    >
      <p className="text-24-sb">{icon}</p>
      <p className="text-black1 text-12-sb">{text}</p>
    </button>
  );
}
