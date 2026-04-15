import { useNavigate } from "react-router-dom";

import Logo from "../components/login/Logo";
import LoginForm from "../components/login/LoginForm";
import LoginButtons from "../components/login/LoginButtons";
import OAuthLoginGroup from "../components/login/OAuthLoginGroup";

// 로그인 페이지
export default function LoginPage() {
    const navigate = useNavigate();

    return (
        <div className="h-screen flex flex-col items-center px-12 pt-24 pb-20 bg-background">
            <Logo />
            <LoginForm />
            <LoginButtons
                onLogin={() => console.log("login")}
                onSignup={() => navigate("/signup")}
            />
            <OAuthLoginGroup />
        </div>
    );
}