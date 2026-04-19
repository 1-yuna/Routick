import { IoReload } from "react-icons/io5";

export default function ReloadButton({ onClick }) {
    return (
        <button
            className="fixed top-5 right-5 z-20 w-12 h-12 rounded-full bg-primary shadow-lg flex items-center justify-center"
            onClick={onClick}
        >
            <IoReload className="w-6 h-6 text-white" />
        </button>
    );
}