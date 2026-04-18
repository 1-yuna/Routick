export default function SaveExitButton({
                                      onExit,
                                      onSave,
                                     // isNextActive = false
                                  }) {
    return (
        <div className="fixed bottom-0 left-0 w-full h-40 bg-white flex justify-around border-t px-4 pt-5">

            {/* 이전 버튼 */}
            <div onClick={onExit} className="w-40 h-16 rounded-md flex justify-center items-center text-base font-bold cursor-pointer border border-black">
                종료
            </div>

            {/* 다음 버튼 */}
            <div onClick={onSave} className="w-40 h-16 text-white bg-primary rounded-md flex justify-center items-center text-base font-bold
                    ">
                저장
            </div>

        </div>
    );
}