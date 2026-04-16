export default function TwoButton({
                                      onPrev,
                                      onNext,
                                      isNextActive = false
                                  }) {
    return (
        <div className="fixed bottom-0 left-0 w-full h-40 bg-white flex justify-around border-t px-4 pt-5">

            {/* 이전 버튼 */}
            <div onClick={onPrev} className="w-40 h-16 bg-primary text-white rounded-md flex justify-center items-center text-base font-bold cursor-pointer">
                이전
            </div>

            {/* 다음 버튼 */}
            <div onClick={isNextActive ? onNext : undefined} className={`w-40 h-16 text-white rounded-md flex justify-center items-center text-base font-bold
                    ${isNextActive
                    ? "bg-primary cursor-pointer"
                    : "bg-primaryLight cursor-not-allowed"
                }`}>
                다음
            </div>

        </div>
    );
}