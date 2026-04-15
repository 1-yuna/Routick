import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHouse, faUser } from "@fortawesome/free-solid-svg-icons"
import {useNavigate, useLocation} from "react-router-dom";

export default function BottomBar() {
    const navigate = useNavigate();
    const location = useLocation();

    const isHome = location.pathname === "/home";
    const isMyPage = location.pathname === "/mypage";

  return (
    <div className="fixed bottom-0 left-0 w-full h-32 bg-white border-t flex justify-around pt-5">
      <button className="flex flex-col items-center text-xs" onClick={() => navigate("/home")}>
          <FontAwesomeIcon className={`w-6 h-6 ${isHome ? "text-primary" : "text-gray-400"}`} icon={faHouse} />
      </button>

      <button className="flex flex-col items-center text-xs" onClick={() => navigate("/mypage")}>
          <FontAwesomeIcon className={`w-6 h-6 ${isMyPage ? "text-primary" : "text-gray-400"}`} icon={faUser} />
      </button>

    </div>
  );
}