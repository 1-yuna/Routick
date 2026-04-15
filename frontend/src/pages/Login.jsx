import logo from "../assets/logo.png";
import naver from "../assets/naver.png";
import kakao from "../assets/kakao.png";
import google from "../assets/google.png";
import CommonInput from "../components/CommonInput.jsx";
import OneButton from "../components/OneButton.jsx";
import OAuthButton from "../components/OAuthButton.jsx";


export default function Login() {
    return (
        <div className="h-screen flex flex-col items-center px-12 pt-24 pb-20 bg-background">
            <img src={logo} className="w-36 h-32 object-contain"/>
            <div className="flex flex-col justify-between pb-12 w-full h-48">
                <CommonInput placeholder="이메일" type="email" />
                <CommonInput placeholder="비밀번호" type="password" />
            </div>
            <OneButton text="로그인" onClick={() => console.log("click")} />
            <div className="flex justify-end p-2 pb-8 w-full" >
                <button className="text-sm text-grayDark" onClick={() => console.log("sign-up") }>회원가입</button>
            </div>
            <div className="flex justify-between w-36">
                <OAuthButton icon={naver} onClick={() => console.log("naver login")}/>
                <OAuthButton icon={kakao} onClick={() => console.log("kakao login")}/>
                <OAuthButton icon={google} onClick={() => console.log("google login")}/>
            </div>

        </div>
    );
}