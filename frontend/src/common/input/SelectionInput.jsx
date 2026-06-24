// 공통 입력창 - onClick 있으면 readOnly(페이지 이동용), 없으면 일반 입력
export default function SelectionInput({
  placeholder,
  value,
  onChange,
  onClick,
  leftIcon,
  rightIcon,
  onKeyDown,
  rounded = 'rounded-10',
}) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center flex-shrink-0 px-3 h-[46px] w-full bg-white border border-line2 ${rounded}`}
    >
      {leftIcon && <div className="mr-3 flex-shrink-0">{leftIcon}</div>}
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        readOnly={!!onClick}
        onChange={onClick ? undefined : onChange}
        onKeyDown={onKeyDown}
        className="w-full text-14-rg text-black1 outline-none placeholder:text-gray1 placeholder:text-14-sb"
      />
      {rightIcon && <div className="ml-2 flex-shrink-0">{rightIcon}</div>}
    </div>
  );
}
