import {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

import main from "../assets/main.png";

export default function SplashPage() {
    const navigate = useNavigate();
    const [fade, setFade] = useState(true);

    useEffect(() => {
        const timer1 = setTimeout(() => {
            setFade(false); // 사라지기 시작
        }, 1000);

        const timer2 = setTimeout(() => {
            navigate("/login"); // 이동
        }, 1500);

        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    }, []);

    return (

        <div
            className={`h-screen flex flex-col justify-between bg-primary pb-24 pt-40 text-white text-2xl font-semibold transition-opacity duration-500 ${
                        fade ? "opacity-100" : "opacity-0"}`}>
            <div className="px-8">
                <p className="mt-2">
                    반갑습니다!
                </p>
                <p className="mt-2">
                    Routick에 오신 것을
                </p>
                <p className="mt-2">
                    환영합니다
                </p>
            </div>
            <div className="flex justify-end">
                <img src={main} className="w-80 h-80 object-contain"/>
            </div>

        </div>
    );
}