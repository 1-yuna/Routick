import FullWidthInput from '../../common/input/FullWidthInput.jsx';

export default function PasswordSection({
  password,
  passwordCheck,
  setPassword,
  setPasswordCheck,
  error,
}) {
  return (
    <>
      {/* Password */}
      <div className="flex flex-col pt-8 mb-4 justify-between h-44">
        <FullWidthInput
          placeholder="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <FullWidthInput
          placeholder="비밀번호 확인"
          type="password"
          value={passwordCheck}
          onChange={(e) => setPasswordCheck(e.target.value)}
        />
      </div>

      {/* Error */}
      {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
    </>
  );
}
