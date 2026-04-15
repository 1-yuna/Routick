import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleLeft } from "@fortawesome/free-solid-svg-icons";

// top-bar + 이전버튼
export default function TopBarButton({ onClick }) {
    return (
        <button onClick={onClick} className="fixed top-0 left-0 w-full h-24 flex items-end px-8">
            <FontAwesomeIcon icon={faAngleLeft} className="text-2xl text-primary"/>
        </button>
    );
}