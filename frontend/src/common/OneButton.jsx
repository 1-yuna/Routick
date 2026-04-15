
// 버튼 1개
export default function OneButton({ text, onClick }) {
    return (
        <button
            onClick={onClick}
            className="w-full h-16 bg-primary text-base text-white flex items-center justify-center"
        >
            {text}
        </button>
    );
}