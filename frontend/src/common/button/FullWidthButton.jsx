// 긴 버튼 1개
export default function FullWidthButton({ text, onClick, className = '' }) {
  return (
    <button
      onClick={onClick}
      className={`w-full h-14 text-16-sb text-white flex items-center justify-center ${className}`}
    >
      {text}
    </button>
  );
}
