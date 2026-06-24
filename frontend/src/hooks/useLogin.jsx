import { useState } from 'react';

// 로그인 관련 상태 및 로직 관리 훅
export default function useLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // 로그인 버튼
  // TODO: API 연동 시 실제 로그인 요청으로 교체
  const handleLogin = (onSuccess) => {
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력해주세요.');
      return;
    }

    // mock: 가입되지 않은 계정 (API 연동 전 임시 처리)
    setError('가입이 안 된 계정입니다');
  };

  return {
    email,
    setEmail,
    password,
    setPassword,
    error,
    setError,
    handleLogin,
  };
}
