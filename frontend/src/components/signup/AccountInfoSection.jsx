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
  setIsVerified,
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
            buttonText="확인"
            onButtonClick={() => setIsVerified(true)}
          />

          <div className="flex justify-between pl-2">
            {!isVerified && (
              <div className="text-gray2 text-14-sb">{formatTime(time)}</div>
            )}
            {isVerified && (
              <div className="text-14-rg text-correct">인증되었습니다.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
