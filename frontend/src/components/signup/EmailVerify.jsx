import CommonInput from "../../common/CommonInput";
import CheckButton from "./CheckButton";

export default function EmailVerify({ showVerify, time, formatTime, setShowVerify, setTime, setIsVerified, isVerified,}) {
    return (
        <>
            {/* Email */}
            <div className="flex pb-4">
                <CommonInput placeholder="이메일" type="email" />
                <CheckButton
                    text="인증"
                    onClick={() => {
                        setShowVerify(true);
                        setTime(120);
                    }}
                />
            </div>

            {/* Verify */}
            {showVerify && (
                <div className="flex flex-col">
                    <div className="flex">
                        <CommonInput placeholder="인증번호" type="text" />
                        <CheckButton
                            text="확인"
                            onClick={() => setIsVerified(true)}
                        />
                    </div>

                    <div className="flex justify-between pl-4 pr-1 py-1">
                        <div className="text-sm text-grayDark">
                            {formatTime(time)}
                        </div>
                        <div className="text-sm text-grayDark">
                            {isVerified && "확인되었습니다."}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}