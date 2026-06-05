import LeftIcon from '../../assets/icons/left.svg?react';

// 지도 상단 바 - 기본 아이콘은 뒤로가기, icon prop으로 변경 가능
export default function MapTopBar({
  onClick,
  text,
  className = '',
  className3 = '',
  icon,
}) {
  // 아이콘 미전달 시 뒤로가기 아이콘 사용
  const Icon = icon || LeftIcon;

  return (
    <div
      className={`z-10 px-6 mt-12 absolute top-0 w-full flex items-center ${className}`}
    >
      {/*왼쪽 - 아이콘 버튼*/}
      <div className="w-1/3 flex items-center justify-start">
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-[2px_2px_1px_0px_rgba(0,0,0,0.25)]"
          onClick={onClick}
        >
          <Icon className="w-4 h-8 text-primary" />
        </button>
      </div>

      {/*가운데 - 빈 공간*/}
      <div className="w-1/3" />

      {/*오른쪽 - 텍스트*/}
      <div className={`w-1/3 flex justify-end ${className3}`}>{text}</div>
    </div>
  );
}
