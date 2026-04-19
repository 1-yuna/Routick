import PlaceCard from "./PlaceCard";
import { IoEllipsisVertical } from "react-icons/io5";

export default function PlaceListItem({ place, isLast, onClick }) {
    return (
        <div className="flex flex-col">
            <PlaceCard
                category={place.category}
                title={place.title}
                time={place.time}
                onClick={onClick}
            />

            {/* 구분 아이콘 */}
            {!isLast && (
                <div className="flex w-32 items-center justify-center text-primary">
                    <IoEllipsisVertical className="w-5 h-5" />
                </div>
            )}
        </div>
    );
}