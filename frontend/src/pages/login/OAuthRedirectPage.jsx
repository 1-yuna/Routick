// pages/login/OAuthRedirectPage.jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe } from '../../api/user';
import useUserStore from '../../store/userStore';

// 소셜 로그인 콜백 착지 페이지 - 딜레이/애니메이션 없이 바로 홈으로
export default function OAuthRedirectPage() {
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await getMe();
        useUserStore.getState().setUser(res.data.data);
        navigate('/home', { replace: true });
      } catch {
        navigate('/login', { replace: true });
      }
    })();
  }, []);

  return null; // 순간적으로 지나가는 화면이라 빈 화면 or 원하면 스피너
}
