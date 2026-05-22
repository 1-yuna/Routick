import { useNavigate } from 'react-router-dom';

import Logo from '../../components/login/Logo.jsx';
import LoginForm from '../../components/login/LoginForm.jsx';
import OAuthLoginGroup from '../../components/login/OAuthLoginGroup.jsx';

// 로그인 페이지
export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="px-6 py-16 h-screen flex flex-col gap-16 items-center bg-login">
      {/*로고*/}
      <Logo className="w-36 h-16 mt-14" />
      {/*입력 폼*/}
      <LoginForm
        onLogin={() => console.log('login')}
        onSignup={() => navigate('/signup')}
      />
      {/*소셜 로그인*/}
      <OAuthLoginGroup />
    </div>
  );
}
