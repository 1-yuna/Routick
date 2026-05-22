// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
// import { faAngleLeft } from '@fortawesome/free-solid-svg-icons';

// top-bar + 이전버튼
export default function TopBarButton({ onClick, children, className = '' }) {
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
