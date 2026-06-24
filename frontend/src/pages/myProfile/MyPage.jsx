// pages/my/MyPage.jsx
import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import PersonIcon from '../../assets/icons/person.svg?react';
import RightIcon from '../../assets/icons/right.svg?react';
import logo from '../../assets/images/logo.png';
import useUserStore from '../../store/userStore.jsx';

// 내 정보 페이지
export default function MyPage() {
  const { user } = useUserStore();
  const navigate = useNavigate();

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-white">
      {/*상단 바*/}
      <TopBar className="px-6">
        <img className="w-22 h-11 object-contain" src={logo} />
      </TopBar>

      <div className="flex flex-col px-6 py-12 gap-14">
        {/*프로필*/}
        <div
          className="flex items-center gap-5 cursor-pointer"
          onClick={() => navigate('/my/profile')}
        >
          <div className="w-14 h-14 rounded-full bg-line1 flex items-center justify-center flex-shrink-0 overflow-hidden">
            {user.src ? (
              <img
                src={user.src}
                alt="프로필"
                className="w-full h-full object-cover"
              />
            ) : (
              <PersonIcon className="w-8 h-8 text-white" />
            )}
          </div>
          <div className="flex items-center gap-1 cursor-pointer">
            <p className="text-16-sb text-black1">{user.name}</p>
            <RightIcon className="w-3 h-6 text-black1" />
          </div>
        </div>

        {/*계정*/}
        <div className="flex flex-col gap-6">
          <p className="text-14-sb text-gray2">계정</p>
          <div className="flex flex-col gap-3">
            <div className="flex justify-between">
              <p className="text-14-rg text-black1">계정 타입</p>
              <p className="text-14-rg text-black1">{user.accountType}</p>
            </div>
            <button
              className="text-left text-14-rg text-red"
              onClick={() => console.log('로그아웃')}
            >
              로그아웃
            </button>
            <button
              className="text-left text-14-rg text-gray2"
              onClick={() => console.log('계정 삭제')}
            >
              계정 삭제
            </button>
          </div>
        </div>
      </div>

      <BottomBar />
    </div>
  );
}
