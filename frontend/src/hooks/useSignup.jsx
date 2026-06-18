import { useState } from 'react';
import useTimer from './useTimer.jsx';
import { useNavigate } from 'react-router-dom';

// 회원가입 관련 상태 및 로직 관리 훅
export default function useSignup() {
  const navigate = useNavigate();

  // 확인, 인증 버튼
  const [showVerify, setShowVerify] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

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

  // 가입 버튼
  const handleSignup = () => {
    if (!password || !passwordCheck) {
      setError('비밀번호를 입력해주세요.');
      return;
    }
    if (password !== passwordCheck) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }
    setError('');
    navigate('/home');
  };

  return {
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
  };
}
