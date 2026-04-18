
export default function TagButton({ label,selected, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`
                flex items-center gap-2 rounded-xl px-4 border
                ${selected
                ? "bg-primary text-white border-primary"
                : "border-primary text-black"}
            `}
        >
            {label}
        </button>
    );
}