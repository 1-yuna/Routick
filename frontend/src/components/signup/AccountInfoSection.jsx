import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import EmailButton from '../../common/button/EmailButton';
import FieldMessage from '../../common/text/FieldMessage.jsx';

// 계정 기본 정보 폼
export default function AccountInfoSection({
  email,
  setEmail,
  emailError,
  onVerifyEmail,
  showVerify,
  time,
  formatTime,
  code,
  setCode,
  codeError,
  onConfirmCode,
  isVerified,
}) {
  return (
    // 계정 기본 정보 묶음
    <div className="flex flex-col gap-3 ">
      {/*닉네임*/}
      <FullWidthInput placeholder="닉네임" type="text" />

      {/*인증*/}
      <div className="flex flex-col gap-1">
        <EmailButton
          placeholder="이메일"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          buttonText="인증"
          onButtonClick={onVerifyEmail}
        />

        {/*이메일 에러 (이미 가입된 계정 등)*/}
        <FieldMessage type="error">{emailError}</FieldMessage>
      </div>

      {/*확인*/}
      {showVerify && (
        <div className="flex flex-col gap-1">
          <EmailButton
            placeholder="인증번호"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            buttonText="확인"
            onButtonClick={onConfirmCode}
          />

          <div className="flex justify-between">
            {/*인증 성공*/}
            {isVerified && (
              <FieldMessage type="success">인증되었습니다</FieldMessage>
            )}

            {/*인증 실패 / 만료 / 시도 초과*/}
            {!isVerified && codeError && (
              <FieldMessage type="error">{codeError}</FieldMessage>
            )}

            {/*에러 없을 때만 타이머 표시*/}
            {!isVerified && !codeError && (
              <div className="text-gray2 text-12-rg pl-3">
                {formatTime(time)}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
