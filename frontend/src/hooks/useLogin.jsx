import { useState } from 'react';
import { login, getErrorMessage } from '../api/auth';
import useUserStore from '../store/userStore';

// 로그인 관련 상태 및 로직 관리 훅
export default function useLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const setUser = useUserStore((state) => state.setUser);

  // 로그인 버튼
  const handleLogin = async (onSuccess) => {
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력해주세요.');
      return;
    }
    try {
      setLoading(true);
      const res = await login(email, password);
      setUser(res.data.data); // 사용자 정보 전역 저장 (쿠키는 자동)
      onSuccess?.();
    } catch (e) {
      setError(getErrorMessage(e, '로그인에 실패했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  return {
    email,
    setEmail,
    password,
    setPassword,
    error,
    setError,
    loading,
    handleLogin,
  };
}
