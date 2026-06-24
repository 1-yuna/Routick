import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import FieldMessage from '../../common/text/FieldMessage.jsx';

// 비밀번호 정보 폼
export default function PasswordSection({
  password,
  passwordCheck,
  setPassword,
  setPasswordCheck,
  error,
}) {
  return (
    <div className="flex flex-col gap-3">
      {/* 비밀번호 */}
      <FullWidthInput
        placeholder="비밀번호"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {/* 비밀번호 확인*/}
      <div className="flex flex-col gap-1">
        <FullWidthInput
          placeholder="비밀번호 확인"
          type="password"
          value={passwordCheck}
          onChange={(e) => setPasswordCheck(e.target.value)}
        />

        {/* Error */}
        <FieldMessage type="error">{error}</FieldMessage>
      </div>
    </div>
  );
}
