import { useNavigate } from "react-router-dom";
import { useState } from "react";

import TopBarButton from "../common/TopBarButton";
import OneButton from "../common/OneButton";

import useTimer from "../hooks/useTimer";
import SignupHeader from "../components/signup/SignupHeader.jsx";
import EmailVerify from "../components/signup/EmailVerify.jsx";
import PasswordSection from "../components/signup/PasswordSection.jsx";

// 회원가입 페이지
export default function SignUpPage() {
    const navigate = useNavigate();

    // 확인, 인증 버튼
    const [showVerify, setShowVerify] = useState(false);
    const [isVerified, setIsVerified] = useState(false);

    // password 체크
    const [password, setPassword] = useState("");
    const [passwordCheck, setPasswordCheck] = useState("");
    const [error, setError] = useState("");

    // 인증 시간
    const { time, setTime } = useTimer(120, showVerify);

    const formatTime = (sec) => {
        const m = String(Math.floor(sec / 60)).padStart(2, "0");
        const s = String(sec % 60).padStart(2, "0");
        return `${m}:${s}`;
    };

    // 회원가입 버튼
    const handleSignup = () => {
        if (password !== passwordCheck) {
            setError("비밀번호가 일치하지 않습니다.");
            return;
        }
        if (!password || !passwordCheck) {
            setError("비밀번호를 입력해주세요.");
            return;
        }

        setError("");
        navigate("/home");
    };

    return (
        <div className="h-screen flex flex-col px-12 bg-background">
            <TopBarButton onClick={() => navigate(-1)} />

            {/* Header */}
            <SignupHeader />

            {/* Email */}
            <EmailVerify
                showVerify={showVerify}
                time={time}
                formatTime={formatTime}
                setShowVerify={setShowVerify}
                setTime={setTime}
                setIsVerified={setIsVerified}
                isVerified={isVerified}
            />

            {/* Password */}
            <PasswordSection
                password={password}
                passwordCheck={passwordCheck}
                setPassword={setPassword}
                setPasswordCheck={setPasswordCheck}
                error={error}
            />

            {/* Submit */}
            <OneButton text="완료" onClick={handleSignup} />
        </div>
    );
}