//import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
//import { faHouse, faUser } from '@fortawesome/free-solid-svg-icons';
//import { useNavigate } from 'react-router-dom';
import HomeIcon from '../../assets/icons/home.svg?react';
import CalendarIcon from '../../assets/icons/calendar.svg?react';
import PersonIcon from '../../assets/icons/person.svg?react';
import BottomBarButton from '../button/BottomBarButton.jsx';

// 하단 바
export default function BottomBar() {
  //const navigate = useNavigate();
  // const location = useLocation();

  //const isHome = location.pathname === '/home';
  //const isMyPage = location.pathname === '/mypage';

  return (
    <div className="fixed bottom-0 left-0 w-full h-[136px] bg-white border-t border-line1 flex gap-[88px] justify-center pt-3">
      <BottomBarButton icon={HomeIcon} label="홈" path="/home" />
      <BottomBarButton icon={CalendarIcon} label="내 여행" path="/mytrip" />
      <BottomBarButton icon={PersonIcon} label="내 정보" path="/mypage" />
    </div>
  );
}
