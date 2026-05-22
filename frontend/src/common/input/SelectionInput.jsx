// 입력창
export default function SelectionInput({
  placeholder,
  value,
  onChange,
  onClick,
  leftIcon,
  rightIcon,
  onKeyDown,
}) {
  return (
    <div
      onClick={onClick}
      className="flex items-center flex-shrink-0 px-4 h-12 w-full bg-white border border-line2 rounded-[10px]"
    >
      {leftIcon && <div className="mr-2 flex-shrink-0">{leftIcon}</div>}
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
