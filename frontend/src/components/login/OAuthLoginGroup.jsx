import OAuthButton from '../../common/button/OAuthButton.jsx';
import naver from '../../assets/images/naver.png';
import kakao from '../../assets/images/kakao.png';
import google from '../../assets/images/google.png';

// 소셜로그인
export default function OAuthLoginGroup() {
  return (
    <div className="flex justify-between gap-4">
      <OAuthButton icon={naver} />
      <OAuthButton icon={kakao} />
      <OAuthButton icon={google} />
    </div>
  );
}
