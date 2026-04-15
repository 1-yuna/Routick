export default function CommonInput({ placeholder, type = "text" }) {
    return (
        <div className="flex items-center px-4 h-16 bg-white">
            <input
                type={type}
                placeholder={placeholder}
                className="w-full text-base text-grayDark outline-none"
            />
        </div>
    );
}