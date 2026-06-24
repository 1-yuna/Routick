// 상단 바
export default function TopBar({
  leftContent,
  onClick,
  title,
  text,
  onTextClick,
  children,
  className = '',
  className3 = '',
}) {
  return (
    <div className={`z-10 top-0 w-full h-14 flex items-center ${className}`}>
      {/* 왼쪽 */}
      <div className="w-1/3 flex items-center justify-start">
        {leftContent ? (
          leftContent
        ) : (
          <button onClick={onClick}>{children}</button>
        )}
      </div>

      {/*가운데 - 타이틀*/}
      <div className="w-1/3 flex justify-center text-16-sb text-black1">
        {title}
      </div>

      {/*오른쪽 - 텍스트 버튼*/}
      <div className={`w-1/3 flex justify-end ${className3}`}>
        <button onClick={onTextClick}>{text}</button>
      </div>
    </div>
  );
}
