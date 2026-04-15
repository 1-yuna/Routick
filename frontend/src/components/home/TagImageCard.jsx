
// Top3에 들어가는 Tag Image
export default function TagImageCard({ image, tags = [],onClick }) {
    return (
        <button onClick={onClick} className="relative flex-shrink-0 h-32 w-52 rounded-xl overflow-hidden shadow-xl">
            <img className="h-full w-full object-cover" src={image} alt="card"/>

            {/* overlay */}
            <div className="absolute inset-0 bg-black/25"></div>

            {/* text */}
            <div className="absolute flex bottom-2 left-2 text-white text-xs font-semibold">
                {tags.map((tag, index) => (
                    <p key={index} className="px-1">
                        #{tag}
                    </p>
                ))}
            </div>

        </button>
    );
}