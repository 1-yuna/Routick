// 저장 폴더
export default function SaveItem({ place, onClick }) {
    return (
        <button
            className="flex items-center h-28 cursor-pointer"
            onClick={onClick}
        >
            <div className="w-28 h-24 mr-5 bg-grayLight" />

            <p className="font-bold text-base">
                {place.title}
            </p>
        </button>
    );
}