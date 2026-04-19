import { useState } from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";
import SaveExitButton from "../common/SaveExitButton.jsx";
import KakaoMap from "../components/map/KakaoMap.jsx";


export default function MapResultPage() {
    const [sheetY, setSheetY] = useState(300); // 초기값 (최소 높이 기준)

    return (
        <div className="relative w-full h-screen overflow-hidden">
            <div
                style={{
                    height: `calc(100vh - ${sheetY}px)`,
                    transition: "height 0.2s ease",
                }}
            >
                <KakaoMap/>
            </div>
            <BottomSheet
                sheetY={sheetY}
                setSheetY={setSheetY}
                initialHeight={350}
                snapPoints={[100, 350, 650]}
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
