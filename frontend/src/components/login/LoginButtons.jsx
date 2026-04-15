import OneButton from "../../common/OneButton.jsx";

// 로그인 버튼
export default function LoginButtons({ onLogin, onSignup }) {
    return (
        <>
            <OneButton text="로그인" onClick={onLogin} />

            <div className="flex justify-end p-2 pb-8 w-full">
                <button
                    className="text-sm text-grayDark"
                    onClick={onSignup}
                >
                    회원가입
                </button>
            </div>
        </>
    );
}