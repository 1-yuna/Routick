import { useNavigate } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';

import Logo from '../../components/login/Logo.jsx';
import LoginForm from '../../components/login/LoginForm.jsx';
import OAuthLoginGroup from '../../components/login/OAuthLoginGroup.jsx';
import useLogin from '../../hooks/useLogin.jsx';
import { useEffect } from 'react';

// 로그인 페이지
export default function LoginPage() {
  const navigate = useNavigate();
  const {
    email,
    setEmail,
    password,
    setPassword,
    error,
    setError,
    handleLogin,
  } = useLogin();
  const [searchParams] = useSearchParams();
  const oauthError = searchParams.get('error');

  useEffect(() => {
    if (oauthError === 'EMAIL_DIFFERENT_PROVIDER')
      setError('다른 방식으로 가입된 이메일입니다');
    else if (oauthError) setError('소셜 로그인에 실패했습니다');
  }, [oauthError]);

  return (
    <div className="px-6 py-16 h-screen flex flex-col gap-16 items-center bg-login">
      {/*로고*/}
      <Logo className="w-36 h-16 mt-14" />
      {/*입력 폼*/}
      <LoginForm
        email={email}
        setEmail={setEmail}
        password={password}
        setPassword={setPassword}
        error={error}
        onLogin={() => handleLogin(() => navigate('/home'))}
        onSignup={() => navigate('/signup')}
      />
      {/*소셜 로그인*/}
      <OAuthLoginGroup />
    </div>
  );
}
