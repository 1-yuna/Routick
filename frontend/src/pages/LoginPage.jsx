import { useNavigate } from 'react-router-dom';

import Logo from '../components/login/Logo';
import LoginForm from '../components/login/LoginForm';
import OAuthLoginGroup from '../components/login/OAuthLoginGroup';

// 로그인 페이지
export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="h-screen flex flex-col gap-16 items-center px-8 py-32 bg-login">
      <Logo className="w-36 h-16" />
      <LoginForm
        onLogin={() => console.log('login')}
        onSignup={() => navigate('/signup')}
      />
      <OAuthLoginGroup />
    </div>
  );
}
