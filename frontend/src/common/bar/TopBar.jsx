// top-bar
export default function TopBar({ onClick, children, className = '' }) {
  return (
    <div className={`sticky top-0 w-full h-14 flex items-center ${className}`}>
      <div className="w-1/3 flex items-center justify-start">
        <button onClick={onClick}>{children}</button>
      </div>
      <div className="w-1/3" />
      <div className="w-1/3" />
    </div>
  );
}
