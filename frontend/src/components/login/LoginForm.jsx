import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';

// 로그인 입력창
export default function LoginForm({ onLogin, onSignup }) {
  return (
    <div className="flex flex-col w-full gap-10">
      <div className="flex flex-col gap-2">
        <FullWidthInput placeholder="이메일" type="email" />
        <FullWidthInput placeholder="비밀번호" type="password" />
      </div>

      <div className="w-full flex flex-col gap-1">
        <FullWidthButton
          text="로그인"
          className="bg-primary"
          onClick={onLogin}
        />
        <button className="self-end text-12-sb text-gray2" onClick={onSignup}>
          회원가입
        </button>
      </div>
    </div>
  );
}
