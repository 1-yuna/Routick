import CommonInput from "../../common/CommonInput.jsx";

// 로그인 입력창
export default function LoginForm() {
    return (
        <div className="flex flex-col justify-between pb-12 w-full h-48">
            <CommonInput placeholder="이메일" type="email" />
            <CommonInput placeholder="비밀번호" type="password" />
        </div>
    );
}