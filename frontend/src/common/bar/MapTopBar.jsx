import LeftIcon from '../../assets/icons/left.svg?react';

// map-top-bar
export default function MapTopBar({
  onClick,
  text,
  className = '',
  className3 = '',
}) {
  return (
    <div
      className={`z-10 px-6 mt-12 absolute top-0 w-full h-18 flex items-center ${className}`}
    >
      <div className="w-1/3 flex items-center justify-start">
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-[2px_2px_1px_0px_rgba(0,0,0,0.25)]"
          onClick={onClick}
        >
          <LeftIcon className="w-5 h-10 text-primary" />
        </button>
      </div>
      <div className="w-1/3" />
      <div className={`w-1/3 flex justify-end ${className3}`}>{text}</div>
    </div>
  );
}
