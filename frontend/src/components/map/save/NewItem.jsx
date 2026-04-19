import { FiPlus } from "react-icons/fi";

export default function NewItem({ onClick }) {
    return (
        <button
            className="flex items-center h-28 cursor-pointer"
            onClick={onClick}
        >
            <div className="flex items-center justify-center w-28 h-24 mr-5 bg-grayLight">
                <FiPlus className="w-8 h-8 text-grayDark" />
            </div>

            <p className="font-bold text-base">
                새 폴더 만들기
            </p>
        </button>
    );
}