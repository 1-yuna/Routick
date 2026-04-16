
// 저장되어 있던 주소
export default function SavedAddress({
                                        address,
                                        isSelected,
                                        onClick
                                    }) {
    return (
        <button
            onClick={onClick}
            className={`flex flex-col justify-center items-start px-6 mb-4 w-full h-28 rounded-md shadow-md transition
                ${isSelected
                ? "border-2 border-primaryDark"
                : "border border-grayLight"
            }
            `}
        >
            <p className="text-base">{address.main}</p>
            <p className="pt-4 text-sm">{address.detail1}</p>
            <p className="text-sm">{address.detail2}</p>
        </button>
    );
}