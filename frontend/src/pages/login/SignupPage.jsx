import { useNavigate } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import SignupHeader from '../../components/signup/SignupHeader.jsx';
import AccountInfoSection from '../../components/signup/AccountInfoSection.jsx';
import PasswordSection from '../../components/signup/PasswordSection.jsx';

import LeftIcon from '../../assets/icons/left.svg?react';
import useSignup from '../../hooks/useSignup.jsx';

// 회원가입 페이지
export default function SignUpPage() {
  const navigate = useNavigate();
  const {
    showVerify,
    setShowVerify,
    isVerified,
    setIsVerified,
    password,
    setPassword,
    passwordCheck,
    setPasswordCheck,
    error,
    time,
    setTime,
    formatTime,
    handleSignup,
  } = useSignup();

  return (
    <div className="px-6 pt-12 pb-24 h-screen flex flex-col bg-login">
      {/*상단 바*/}
      <TopBar className="bg-login" onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="flex flex-col gap-8 pt-8">
        {/* 헤더 */}
        <SignupHeader />

        {/* 기본 정보 폼 */}
        <AccountInfoSection
          showVerify={showVerify}
          time={time}
          formatTime={formatTime}
          setShowVerify={setShowVerify}
          setTime={setTime}
          setIsVerified={setIsVerified}
          isVerified={isVerified}
        />

        {/* 비밀번호 정보 폼 */}
        <PasswordSection
          password={password}
          passwordCheck={passwordCheck}
          setPassword={setPassword}
          setPasswordCheck={setPasswordCheck}
          error={error}
        />
      </div>

      {/* 하단 버튼 */}
      <FullWidthButton
        text="완료"
        className="bg-primary mt-auto"
        onClick={handleSignup}
      />
    </div>
  );
}
