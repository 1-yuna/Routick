import OAuthButton from '../../common/button/OAuthButton.jsx';
import naver from '../../assets/images/naver.png';
import kakao from '../../assets/images/kakao.png';
import google from '../../assets/images/google.png';

const OAUTH_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/auth/oauth`;

// 소셜로그인 — 백엔드 OAuth 시작 주소로 페이지 이동 (axios 아님, 리다이렉트 흐름)
export default function OAuthLoginGroup() {
  const handleOAuth = (provider) => {
    window.location.href = `${OAUTH_BASE_URL}/${provider}`;
  };

  return (
    <div className="flex justify-between gap-4">
      <OAuthButton
        icon={naver}
        alt="네이버 로그인"
        onClick={() => handleOAuth('naver')}
      />
      <OAuthButton
        icon={kakao}
        alt="카카오 로그인"
        onClick={() => handleOAuth('kakao')}
      />
      <OAuthButton
        icon={google}
        alt="구글 로그인"
        onClick={() => handleOAuth('google')}
      />
    </div>
  );
}
