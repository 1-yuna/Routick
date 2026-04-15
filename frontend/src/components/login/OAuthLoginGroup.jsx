import OAuthButton from "./OAuthButton.jsx";
import naver from "../../assets/naver.png";
import kakao from "../../assets/kakao.png";
import google from "../../assets/google.png";

// 소셜로그인
export default function OAuthLoginGroup() {
    return (
        <div className="flex justify-between w-36">
            <OAuthButton icon={naver} />
            <OAuthButton icon={kakao} />
            <OAuthButton icon={google} />
        </div>
    );
}