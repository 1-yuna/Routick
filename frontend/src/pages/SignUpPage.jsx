import {useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";

import TopBarButton from "../common/TopBarButton.jsx";
import CommonInput from "../common/CommonInput.jsx";
import CheckButton from "../components/signUp/CheckButton.jsx";
import OneButton from "../common/OneButton.jsx";

export default function SignUpPage() {
    const navigate = useNavigate();
    const [showVerify, setShowVerify] = useState(false);
    const [time, setTime] = useState(120);
    const [isVerified, setIsVerified] = useState(false);

    const [password, setPassword] = useState("");
    const [passwordCheck, setPasswordCheck] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        if (!showVerify) return;

        const timer = setInterval(() => {
            setTime((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [showVerify]);

    const formatTime = (sec) => {
        const m = String(Math.floor(sec / 60)).padStart(2, "0");
        const s = String(sec % 60).padStart(2, "0");
        return `${m}:${s}`;
    };

    return (
        <div className="h-screen flex flex-col px-12 bg-background">
            <TopBarButton onClick={() => navigate(-1)}/>
            <div className="flex flex-col mt-40 pb-12 text-xl font-bold">
                <p>어서오세요!</p>
                <p>회원가입을 진행해주세요</p>
            </div>

            <div className="flex pb-4">
                <CommonInput placeholder="이메일" type="email"/>
                <CheckButton text="인증" onClick={() => {
                    setShowVerify(true);
                    setTime(120);
                }}/>
            </div>
            {showVerify && (
                <div className="flex flex-col">
                    <div className="flex ">
                        <CommonInput placeholder="인증번호" type="text"/>
                        <CheckButton text="확인" onClick={() => setIsVerified(true)}/>
                    </div>

                    <div className="flex justify-between pl-4 pr-1 py-1">
                        <div className="text-sm text-grayDark">{formatTime(time)}</div>
                        <div className="text-sm text-grayDark">{isVerified ? "확인되었습니다." : ""}</div>
                    </div>
                </div>
            )}


            <div className="flex flex-col pt-8 mb-16 justify-between h-44">
                <CommonInput
                    placeholder="비밀번호"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <CommonInput
                    placeholder="비밀번호 확인"
                    type="password"
                    value={passwordCheck}
                    onChange={(e) => setPasswordCheck(e.target.value)}
                />
            </div>
            <OneButton
                text="완료"
                onClick={() => {
                    if (password === passwordCheck) {
                        setError("");
                        navigate("/home"); // 또는 "/"
                    } else {
                        setError("비밀번호가 일치하지 않습니다.");
                    }
                }}
            />

            {error && (
                <div className="text-sm text-red-500 mb-2">
                    {error}
                </div>
            )}


        </div>

    );
}