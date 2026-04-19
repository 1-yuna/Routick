import {useState} from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";
import SaveExitButton from "../common/SaveExitButton.jsx";
import KakaoMap from "../components/map/KakaoMap.jsx";
import MapContainer from "../components/map/MapContainer.jsx";
import ReloadButton from "../components/map/ReloadButton.jsx";
import PlaceListItem from "../components/map/PlaceListItem.jsx";
import SaveBottomSheet from "../components/map/save/SaveBottomSheet.jsx";
import {useNavigate} from "react-router-dom";
import ExitModal from "../components/map/ExitModal.jsx";

export default function MapResultPage() {
    const [sheetY, setSheetY] = useState(300);
    const [isOpen, setOpen] = useState(false);
    const [isExitOpen, setIsExitOpen] = useState(false);
    const navigate = useNavigate();

    // mock
    const places = [
        {
            id: 1,
            category: "카페",
            title: "타코잇 상수역점",
            time: "10:00~12:00",
        },
        {
            id: 2,
            category: "카페",
            title: "블루보틀 성수점",
            time: "09:00~11:00",
        },
        {
            id: 3,
            category: "카페",
            title: "스타벅스 강남점",
            time: "08:00~10:00",
        },
    ];


    return (
        <div className="relative w-full h-screen overflow-hidden">
            {/*map*/}
            <MapContainer sheetY={sheetY}>
                <KakaoMap/>
            </MapContainer>

            {/*새로고침*/}
            <ReloadButton onClick={() => console.log("버튼 클릭")}/>

            {/*바텀시트*/}
            <BottomSheet
                sheetY={sheetY}
                setSheetY={setSheetY}
                initialHeight={300}
                snapPoints={[100, 300, 650]}
                maxHeightPercent={90}
            >
                <div>
                    {places.map((place, index) => (
                        <PlaceListItem
                            key={place.id}
                            place={place}
                            isLast={index === places.length - 1}
                            onClick={() => console.log(place.title)}
                        />
                    ))}
                </div>


            </BottomSheet>

            {/*버튼*/}
            <SaveExitButton
                onExit={() => setIsExitOpen(true)}
                onSave={() => setOpen(true)}
                // isNextActive={isNextActive}
            />

            {/*저장시, 바텀시트*/}
            <SaveBottomSheet
                isOpen={isOpen}
                setOpen={setOpen}
                onSave={() => console.log("저장 실행")}
            />

            {/*종료시, 모달창*/}
            <ExitModal
                isOpen={isExitOpen}
                setOpen={setIsExitOpen}
                onExit={() => {
                    navigate("/home");  // 종료 확정 시 이동
                }}
            />
        </div>
    );
}
