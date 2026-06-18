import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import FieldMessage from '../../common/text/FieldMessage.jsx';

// 로그인 폼
export default function LoginForm({
  email,
  setEmail,
  password,
  setPassword,
  error,
  onLogin,
  onSignup,
}) {
  return (
    <div className="flex flex-col w-full gap-11">
      {/*입력창*/}
      <div className="relative flex flex-col gap-2">
        <FullWidthInput
          placeholder="이메일"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <FullWidthInput
          placeholder="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {/*로그인 에러*/}
        <div className="absolute top-full left-0 mt-1">
          <FieldMessage type="error">{error}</FieldMessage>
        </div>
      </div>

      {/*버튼*/}
      <div className="w-full flex flex-col gap-2">
        <FullWidthButton
          text="로그인"
          className="bg-primary"
          onClick={onLogin}
        />
        <button
          className="px-3 self-end text-12-sb text-gray2"
          onClick={onSignup}
        >
          회원가입
        </button>
      </div>
    </div>
  );
}
