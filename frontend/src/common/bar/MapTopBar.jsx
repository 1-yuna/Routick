import LeftIcon from '../../assets/icons/left.svg?react';

// map-top-bar
export default function MapTopBar({
  onClick,
  text,
  className = '',
  className3 = '',
  icon,
}) {
  const Icon = icon || LeftIcon;

  return (
    <div
      className={`z-10 px-6 mt-12 absolute top-0 w-full flex items-center ${className}`}
    >
      <div className="w-1/3 flex items-center justify-start">
        <button
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-[2px_2px_1px_0px_rgba(0,0,0,0.25)]"
          onClick={onClick}
        >
          <Icon className="w-4 h-8 text-primary" />
        </button>
      </div>
      <div className="w-1/3" />
      <div className={`w-1/3 flex justify-end ${className3}`}>{text}</div>
    </div>
  );
}
