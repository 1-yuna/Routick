import TopBarLogo from "../common/TopBarLogo.jsx";
import TwoButton from "../common/TwoButton.jsx";
import {useNavigate} from "react-router-dom";
import TagSelectGroup from "../components/course-preference-detail/TagSelectGroup.jsx";
import {useState} from "react";

export default function CoursePreferenceDetailPage() {
    const navigate = useNavigate();
    const [themes, setThemes] = useState([]);
    const [activities, setActivities] = useState([]);

    // 하나 이상 선택 -> true
    const isNextActive = themes.length > 0 && activities.length > 0;

    return (
        <div className="flex flex-col px-9 pt-32 pb-40 bg-backgroundLight">
            <TopBarLogo />
            <TagSelectGroup
                question="어떤 분위기의 여행을 원하나요?"
                description="(중복 선택 가능)"
                value={themes}
                onChange={setThemes}
                options={[
                    { value: "healing", label: "힐링" },
                    { value: "clean", label: "깔끔한" },
                    { value: "vintage", label: "빈티지" },
                    { value: "lively", label: "활기찬" },
                    { value: "hip", label: "힙한" },
                    { value: "unique", label: "이색" },
                    { value: "emotional", label: "감성" },
                ]}
            />
            <TagSelectGroup
                question="어떤 활동을 즐기고 싶나요?"
                description="(중복 선택 가능)"
                value={activities}
                onChange={setActivities}
                options={[
                    { value: "cafe", label: "카페" },
                    { value: "exhibition", label: "전시관" },
                    { value: "experience", label: "체험관" },
                    { value: "camping", label: "캠핑장" },
                    { value: "bar", label: "술집" },
                    { value: "theater", label: "극장" },
                    { value: "market", label: "마켓" },
                ]}
            />

            <TwoButton
                onPrev={() => navigate(-1)}
                onNext={() => navigate("/map")}
                isNextActive={isNextActive}
            />
        </div>
    );
}