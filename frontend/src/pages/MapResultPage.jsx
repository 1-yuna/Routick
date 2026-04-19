import { useState } from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";
import SaveExitButton from "../common/SaveExitButton.jsx";
import KakaoMap from "../components/map/KakaoMap.jsx";


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
            <BottomSheet
                initialHeight={500}
                snapPoints={[250, 500, 800]}
                maxHeightPercent={90}
            >
                <div className="space-y-4">
                    {Array.from({length: 20}).map((_, i) => (
                        <div
                            key={i}
                            className="h-20 bg-gray-200 rounded-lg"
                        />
                    ))}
                </div>
            </BottomSheet>

            <SaveExitButton
                onExit={() => console.log("Exit")}
                onSave={() => console.log("Save")}
                // isNextActive={isNextActive}
            />


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