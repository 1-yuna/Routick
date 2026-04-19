import {useState} from "react";
import BottomSheet from "../components/map/BottomSheet.jsx";
import SaveExitButton from "../common/SaveExitButton.jsx";
import KakaoMap from "../components/map/KakaoMap.jsx";
import MapContainer from "../components/map/MapContainer.jsx";
import ReloadButton from "../components/map/ReloadButton.jsx";
import PlaceListItem from "../components/map/PlaceListItem.jsx";

export default function MapResultPage() {
    const [sheetY, setSheetY] = useState(300);

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
                onExit={() => console.log("Exit")}
                onSave={() => console.log("Save")}
                // isNextActive={isNextActive}
            />
        </div>
    );
}
