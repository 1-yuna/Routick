
// 입력창
export default function CommonInput({ placeholder, type, value, onChange }) {
    return (
        <div className="flex items-center px-4 h-16 w-full bg-white">
            <input
                type={type}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                className="w-full text-base text-grayDark outline-none"
            />
        </div>
    );
}