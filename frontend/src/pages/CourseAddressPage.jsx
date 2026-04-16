import {useNavigate} from "react-router-dom";
import TopBarLogo from "../common/TopBarLogo.jsx";
import TwoButton from "../common/TwoButton.jsx";
import {useState} from "react";
import {CgAdd} from "react-icons/cg";

export default function CourseAddressPage() {
    const navigate = useNavigate();

    // 현재 선택된 버튼 id
    const [selectedId, setSelectedId] = useState(null);

    // 선택된 버튼이 존재하면 true
    const isNextActive = selectedId !== null;

    // 이전 버튼 && 현재 버튼이 같으면 해제해야하니 null
    const handleSelect = (id) => {
        setSelectedId(prev => (prev === id ? null : id));
    };

    // mock데이터
    const mockAddresses = [
        {
            id: 1,
            main: "인천 서구 장고개로 319",
            detail1: "인천 서구 장고개로 310 진주아파트",
            detail2: "502동 1003호"
        },
        {
            id: 2,
            main: "서울 강남구 테헤란로 123",
            detail1: "삼성빌딩",
            detail2: "10층"
        },
        {
            id: 3,
            main: "부산 해운대구 센텀중앙로 45",
            detail1: "센텀타워",
            detail2: "1201호"
        },
        {
            id: 4,
            main: "부산 해운대구 센텀중앙로 45",
            detail1: "센텀타워",
            detail2: "1201호"
        }
    ];


    return (
        <div className="px-9 pt-40 pb-40 bg-backgroundLight">
            <TopBarLogo onClick={() => console.log("편집")} isEdit={true}/>

            <button onClick={() => handleSelect(0)}
                    className={`flex flex-col mb-4 justify-center items-center w-full h-28 bg-transparent border-2 border-grayLight text-grayDark rounded-md shadow-md ${selectedId === 0
                        ? "bg-transparent border-2 border-primaryDark border-solid"
                        : "bg-transparent border-2 border-grayLight border-dashed "
                    }
    `}>
                <CgAdd className="w-7 h-7"/>
                <p className="text-sm pt-1">장소 검색 추가하기</p>
            </button>


            {mockAddresses.map((item) => (
                <button
                    key={item.id}
                    onClick={() => handleSelect(item.id)}
                    className={`flex flex-col justify-center items-start px-6 mb-4 w-full h-28 rounded-md shadow-md transition
            ${selectedId === item.id
                        ? "border-2 border-primaryDark"
                        : "border border-grayLight"
                    }
        `}
                >
                    <p className="text-base">{item.main}</p>
                    <p className="pt-4 text-sm">{item.detail1}</p>
                    <p className="text-sm">{item.detail2}</p>
                </button>
            ))}

            <TwoButton
                onPrev={() => navigate(-1)}
                onNext={() => navigate("/next-page")}
                isNextActive={isNextActive}
            />

        </div>
    );
}