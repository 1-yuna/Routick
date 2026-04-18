import { useState } from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";


export default function MapResultPage() {
    const [open, setOpen] = useState(false);

    return (
        <div className="p-5">
            <button
                className="px-4 py-2 bg-black text-white rounded-lg"
                onClick={() => setOpen(true)}
            >
                바텀시트 열기
            </button>

            <BottomSheet isOpen={open} setOpen={setOpen}>
                <div className="space-y-3">
                    <h2 className="text-lg font-bold">바텀시트</h2>
                    <p className="text-gray-600">
                        react-modal-sheet + tailwind 구성 예시다.
                    </p>

                    <button
                        className="w-full py-2 bg-blue-500 text-white rounded"
                        onClick={() => setOpen(false)}
                    >
                        닫기
                    </button>
                </div>
            </BottomSheet>
        </div>
    );
}



{/*<SaveExitButton*/}
{/*    onExit={() => console.log("Exit")}*/}
{/*    onSave={() => console.log("Save")}*/}
{/*    //isNextActive={isNextActive}*/}
{/*/>*/}