import { FaRegCalendarAlt } from "react-icons/fa";

export default function PlaceCard({
                                      category,
                                      title,
                                      time,
                                      onClick,
                                  }) {
    return (
        <div className="flex my-4 h-32">
            {/* 썸네일 */}
            <div className="w-32 aspect-square mr-5 bg-grayLight" />

            {/* 내용 */}
            <div className="flex flex-col flex-1 justify-between">
                <div>
                    <span className="inline-block px-3 py-1 mb-1 bg-primaryLight text-xs text-primary rounded-xl">
                        {category}
                    </span>

                    <p className="font-bold text-base">{title}</p>

                    <div className="flex items-center text-sm">
                        <FaRegCalendarAlt className="mr-2" />
                        {time}
                    </div>
                </div>

                <button
                    onClick={onClick}
                    className="w-24 py-1 bg-primary text-white rounded-md">
                    바로가기
                </button>
            </div>
        </div>
    );
}