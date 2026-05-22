import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import EmailButton from '../../common/button/EmailButton';

// 계정 기본 정보 폼
export default function AccountInfoSection({
  showVerify,
  time,
  formatTime,
  setShowVerify,
  setTime,
  setIsVerified,
  isVerified,
}) {
  return (
    // 계정 기본 정보 묶음
    <div className="flex flex-col gap-3 ">
      {/*닉네임*/}
      <FullWidthInput placeholder="닉네임" type="text" />

      {/*인증*/}
      <EmailButton
        placeholder="이메일"
        type="email"
        buttonText="인증"
        onButtonClick={() => {
          setShowVerify(true);
          setTime(120);
        }}
      />

      {/*확인*/}
      {showVerify && (
        <div className="flex flex-col gap-2">
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
