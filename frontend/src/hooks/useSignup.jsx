import { useState } from 'react';
import useTimer from '../hooks/useTimer';
import { useNavigate } from 'react-router-dom';

// 인증 시도 최대 횟수
const MAX_VERIFY_ATTEMPTS = 3;
const EXPIRED_MESSAGE = '인증번호가 만료되었습니다. 다시 요청해주세요';

// 회원가입 관련 상태 및 로직 관리 훅
export default function useSignup() {
  const navigate = useNavigate();

  // 이메일
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  // 확인, 인증 버튼
  const [showVerify, setShowVerify] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  // 인증번호
  const [code, setCode] = useState('');
  const [codeError, setCodeError] = useState('');
  const [attemptCount, setAttemptCount] = useState(0);

  // password 체크
  const [password, setPassword] = useState('');
  const [passwordCheck, setPasswordCheck] = useState('');
  const [error, setError] = useState('');
  const { time, setTime } = useTimer(120, showVerify);

  // 인증 시간
  const formatTime = (sec) => {
    const m = String(Math.floor(sec / 60)).padStart(2, '0');
    const s = String(sec % 60).padStart(2, '0');
    return `${m}:${s}`;
  };

  // 화면에 보여줄 최종 에러 - 시간이 만료됐으면 만료 메시지가 항상 우선
  // (effect 없이 렌더링 시점에 계산하는 파생값)
  const displayedCodeError =
    showVerify && !isVerified && time === 0 ? EXPIRED_MESSAGE : codeError;

  // 이메일 인증 버튼
  // TODO: API 연동 시 실제 이메일 중복 확인 요청으로 교체
  const handleVerifyEmail = () => {
    if (!email) {
      setEmailError('이메일을 입력해주세요.');
      return;
    }

    // mock: 이메일에 'kakao'가 포함되면 이미 가입된 계정으로 처리
    if (email.includes('kakao')) {
      setEmailError('이미 가입된 계정입니다');
      setShowVerify(false);
      return;
    }

    setEmailError('');
    setShowVerify(true);
    setIsVerified(false);
    setCode('');
    setCodeError('');
    setAttemptCount(0);
    setTime(120);
  };

  // 인증번호 확인 버튼
  // TODO: API 연동 시 실제 인증번호 확인 요청으로 교체
  const handleConfirmCode = () => {
    // 이미 시간이 만료된 상태면 더 이상 시도 불가
    if (time === 0) {
      return;
    }

    // mock: 인증번호가 '1234'면 성공
    if (code === '1234') {
      setIsVerified(true);
      setCodeError('');
      return;
    }

    // 틀렸을 때 - 시도 횟수 누적
    const nextCount = attemptCount + 1;
    setAttemptCount(nextCount);

    if (nextCount >= MAX_VERIFY_ATTEMPTS) {
      setCodeError('인증 시도 횟수를 초과했습니다. 다시 요청해주세요');
    } else {
      setCodeError('인증번호가 일치하지 않습니다');
    }
  };

  // 비밀번호 형식 - 8자 이상, 영문/숫자 포함
  const isValidPasswordFormat = (value) =>
    value.length >= 8 && /[a-zA-Z]/.test(value) && /[0-9]/.test(value);

  // 가입 버튼
  const handleSignup = () => {
    if (!isVerified) {
      if (showVerify) {
        // 인증 버튼은 눌렀지만 인증번호 확인을 안 마친 상태
        setCodeError('이메일 인증을 완료해주세요');
      } else {
        // 인증 버튼 자체를 누르지 않은 상태
        setEmailError('이메일 인증을 완료해주세요');
      }
      return;
    }
    if (!password || !passwordCheck) {
      setError('비밀번호를 입력해주세요.');
      return;
    }
    if (!isValidPasswordFormat(password)) {
      setError('8자 이상, 영문/숫자를 포함해주세요');
      return;
    }
    if (password !== passwordCheck) {
      setError('비밀번호가 일치하지 않습니다');
      return;
    }
    setError('');
    navigate('/home');
  };

  return {
    email,
    setEmail,
    emailError,
    handleVerifyEmail,
    showVerify,
    setShowVerify,
    isVerified,
    setIsVerified,
    code,
    setCode,
    codeError: displayedCodeError,
    handleConfirmCode,
    password,
    setPassword,
    passwordCheck,
    setPasswordCheck,
    error,
    time,
    setTime,
    formatTime,
    handleSignup,
  };
}
