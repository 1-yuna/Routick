// pages/myProfile/MyPage.jsx
import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import PersonIcon from '../../assets/icons/person.svg?react';
import RightIcon from '../../assets/icons/right.svg?react';
import logo from '../../assets/images/logo.png';
import useUserStore from '../../store/userStore.jsx';
import { logout } from '../../api/auth.jsx';
import { deleteMe } from '../../api/user.jsx';
import { getImageUrl } from '../../utils/imageUtil.jsx';

const PROVIDER_LABEL = {
  local: '이메일',
  kakao: '카카오',
  naver: '네이버',
  google: '구글',
};

// 내 정보 페이지
export default function MyPage() {
  const { user, clearUser } = useUserStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (e) {
      // 서버 로그아웃 실패해도 클라이언트 상태는 정리
    } finally {
      clearUser();
      navigate('/login');
    }
  };

  const handleDeleteAccount = async () => {
    if (
      !window.confirm(
        '정말 탈퇴하시겠습니까? 여행·선호도 데이터가 모두 삭제됩니다.'
      )
    )
      return;
    try {
      await deleteMe();
    } catch (e) {
      alert('탈퇴에 실패했습니다. 잠시 후 다시 시도해주세요.');
      return;
    }
    clearUser();
    navigate('/login');
  };

  if (!user) return null; // 로그아웃/탈퇴 처리 중 null 렌더 방지

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-white">
      <TopBar className="px-6">
        <img className="w-22 h-11 object-contain" src={logo} />
      </TopBar>

      <div className="flex flex-col px-6 py-12 gap-14">
        <div
          className="flex items-center gap-5 cursor-pointer"
          onClick={() => navigate('/my/profile')}
        >
          <div className="w-14 h-14 rounded-full bg-line1 flex items-center justify-center flex-shrink-0 overflow-hidden">
            {user.profileImageUrl ? (
              <img
                src={getImageUrl(user.profileImageUrl)}
                alt="프로필"
                className="w-full h-full object-cover"
              />
            ) : (
              <PersonIcon className="w-8 h-8 text-white" />
            )}
          </div>
          <div className="flex items-center gap-1 cursor-pointer">
            <p className="text-16-sb text-black1">{user.nickname}</p>
            <RightIcon className="w-3 h-6 text-black1" />
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <p className="text-14-sb text-gray2">계정</p>
          <div className="flex flex-col gap-3">
            <div className="flex justify-between">
              <p className="text-14-rg text-black1">계정 타입</p>
              <p className="text-14-rg text-black1">
                {PROVIDER_LABEL[user.provider] ?? user.provider}
              </p>
            </div>
            <button
              className="text-left text-14-rg text-red"
              onClick={handleLogout}
            >
              로그아웃
            </button>
            <button
              className="text-left text-14-rg text-gray2"
              onClick={handleDeleteAccount}
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
