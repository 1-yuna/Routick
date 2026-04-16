import { CgAdd } from "react-icons/cg";

// 주소 생성
export default function NewAddress({
                                       isSelected,
                                       onClick
                                   }) {
    return (
        <button
            onClick={onClick}
            className={`flex flex-col mb-4 justify-center items-center w-full h-28 rounded-md shadow-md transition
                ${isSelected
                ? "border-2 border-primaryDark border-solid"
                : "border-2 border-grayLight border-dashed text-grayDark"
            }
            `}
        >
            <CgAdd className="w-7 h-7"/>
            <p className="text-sm pt-1">장소 검색 추가하기</p>
        </button>
    );
}