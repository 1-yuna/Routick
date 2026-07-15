import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useTimer from '../hooks/useTimer';
import {
  sendEmailCode,
  verifyEmailCode,
  signup,
  login,
  getErrorMessage,
} from '../api/auth';
import useUserStore from '../store/userStore';

const EXPIRED_MESSAGE = '인증번호가 만료되었습니다. 다시 요청해주세요';

// 회원가입 관련 상태 및 로직 관리 훅
export default function useSignup() {
  const navigate = useNavigate();
  const setUser = useUserStore((state) => state.setUser);

  // 닉네임
  const [nickname, setNickname] = useState('');
  const [nicknameError, setNicknameError] = useState('');

  // 이메일
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  // 확인, 인증 버튼
  const [showVerify, setShowVerify] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  // 인증번호
  const [code, setCode] = useState('');
  const [codeError, setCodeError] = useState('');

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

  // 시간이 만료됐으면 만료 메시지가 항상 우선
  const displayedCodeError =
    showVerify && !isVerified && time === 0 ? EXPIRED_MESSAGE : codeError;

  // 이메일 인증 버튼 — 가입 여부 확인 + 인증번호 발송
  const handleVerifyEmail = async () => {
    if (!email) {
      setEmailError('이메일을 입력해주세요.');
      return;
    }
    try {
      await sendEmailCode(email);
      setEmailError('');
      setShowVerify(true);
      setIsVerified(false);
      setCode('');
      setCodeError('');
      setTime(120);
    } catch (e) {
      // EMAIL_ALREADY_EXISTS / EMAIL_DIFFERENT_PROVIDER 등 서버 메시지 그대로 표시
      setEmailError(getErrorMessage(e));
      setShowVerify(false);
    }
  };

  // 인증번호 확인 버튼 — 시도 횟수 제한(5회)은 서버가 관리
  const handleConfirmCode = async () => {
    if (time === 0) return;
    try {
      await verifyEmailCode(email, code);
      setIsVerified(true);
      setCodeError('');
    } catch (e) {
      // CODE_MISMATCH / CODE_EXPIRED / CODE_ATTEMPT_EXCEEDED 서버 메시지 그대로 표시
      setCodeError(getErrorMessage(e));
    }
  };

  // 비밀번호 형식 - 8자 이상, 영문/숫자 포함
  const isValidPasswordFormat = (value) =>
    value.length >= 8 && /[a-zA-Z]/.test(value) && /[0-9]/.test(value);

  // 가입 버튼 — 성공 시 자동 로그인 후 홈으로
  const handleSignup = async () => {
    if (!nickname || nickname.length < 2 || nickname.length > 10) {
      setNicknameError('닉네임은 2~10자로 입력해주세요');
      return;
    }
    setNicknameError('');
    if (!isVerified) {
      if (showVerify) setCodeError('이메일 인증을 완료해주세요');
      else setEmailError('이메일 인증을 완료해주세요');
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
    try {
      setError('');
      await signup(nickname, email, password);
      const res = await login(email, password); // 가입 직후 자동 로그인 (쿠키 발급)
      setUser(res.data.data);
      navigate('/home');
    } catch (e) {
      setError(getErrorMessage(e));
    }
  };

  return {
    nickname,
    setNickname,
    nicknameError,
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
