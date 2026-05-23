// top-bar
export default function TopBar({
  onClick,
  text,
  children,
  className = '',
  className3 = '',
}) {
  return (
    <div className={`z-10 top-0 w-full h-14 flex items-center ${className}`}>
      <div className="w-1/3 flex items-center justify-start">
        <button onClick={onClick}>{children}</button>
      </div>
      <div className="w-1/3" />
      <div className={`w-1/3 flex justify-end ${className3}`}>{text}</div>
    </div>
  );
}
