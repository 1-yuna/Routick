// 공통 입력창
export default function FullWidthInput({ placeholder, type, value, onChange }) {
  return (
    <div className="flex items-center px-3 h-14 w-full bg-white border border-line1">
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="w-full text-16-rg text-gray2 outline-none placeholder:text-gray1 placeholder:text-16-sb"
      />
    </div>
  );
}
