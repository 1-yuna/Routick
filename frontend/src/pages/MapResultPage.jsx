import { useState } from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";
import SaveExitButton from "../common/SaveExitButton.jsx";


export default function MapResultPage() {
    //const [open, setOpen] = useState(false);

    return (
        <div className="p-5">
            {/*<button*/}
            {/*    className="px-4 py-2 bg-black text-white rounded-lg"*/}
            {/*    onClick={() => setOpen(true)}*/}
            {/*>*/}
            {/*    바텀시트 열기*/}
            {/*</button>*/}

            {/* 항상 떠 있는 바텀시트 */}
            <BottomSheet>
                <div className="space-y-3">
                    <h2 className="text-lg font-bold">필터 / 정보 영역</h2>

                    <p className="text-gray-600">
                        이 영역은 항상 존재하고 높이만 조절된다
                    </p>

                    <button className="w-full py-2 bg-blue-500 text-white rounded">
                        액션 버튼
                    </button>
                </div>
            </BottomSheet>

           {/*<SaveExitButton*/}
           {/*onExit={() => console.log("Exit")}*/}
           {/*onSave={() => console.log("Save")}*/}
           {/*  // isNextActive={isNextActive}*/}
           {/*/>*/}



        </div>
    );
}


{/*<SaveExitButton*/
}
{/*    onExit={() => console.log("Exit")}*/
}
{/*    onSave={() => console.log("Save")}*/
}
{/*    //isNextActive={isNextActive}*/
}
{/*/>*/
}