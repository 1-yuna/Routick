import TagImageCard from "./TagImageCard";

// Top3
export default function TopCardSection({ title, items = [] , onClick}) {
    return (
        <div className="flex flex-col pt-8">

            <p className="font-bold text-base py-4">{title}</p>

            <div className="flex overflow-x-auto gap-4 px-2 no-scrollbar">
                {items.map((item, index) => (
                    <TagImageCard
                        key={index}
                        image={item.image}
                        tags={item.tags}
                        onClick={onClick}
                    />
                ))}
            </div>

        </div>
    );
}