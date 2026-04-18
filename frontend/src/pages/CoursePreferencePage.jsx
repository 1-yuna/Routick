import TopBarLogo from "../common/TopBarLogo.jsx";
import TwoButton from "../common/TwoButton.jsx";
import {useNavigate} from "react-router-dom";
import {useState} from "react";
import RadioGroup from "../components/course-preference/RadioGroup.jsx";

export default function CoursePreferencePage() {
    const navigate = useNavigate();
    const [companion, setCompanion] = useState("");
    const [gender, setGender] = useState("");
    const [groupSize, setGroupSize] = useState("");
    const [ageGroup, setAgeGroup] = useState("");
    const [duration, setDuration] = useState("");

    // 모두 선택 -> true
    const isNextActive = [companion && gender && groupSize && ageGroup && duration].every(Boolean);

    return (
        <div className="flex flex-col px-9 pt-32 pb-40 bg-backgroundLight">
            <TopBarLogo />
            <RadioGroup
                question="이번 여행은 누구와 함께 떠나나요?"
                name="companion"
                value={companion}
                onChange={(e) => setCompanion(e.target.value)}
                options={[
                    { value: "solo", label: "혼자" },
                    { value: "couple", label: "연인" },
                    { value: "friends", label: "친구" },
                    { value: "family", label: "가족" },
                    { value: "group", label: "동호회" },
                ]}
            />
            <RadioGroup
                question="성별 구성이 어떻게 되나요?"
                name="gender"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                options={[
                    { value: "male", label: "남자" },
                    { value: "female", label: "여자" },
                    { value: "mixed", label: "혼성" },
                ]}
            />
            <RadioGroup
                question="총 몇명이 함께 하나요?"
                name="groupSize"
                value={groupSize}
                onChange={(e) => setGroupSize(e.target.value)}
                options={[
                    { value: "one", label: "1명" },
                    { value: "two", label: "2명" },
                    { value: "threeToFour", label: "3~4명" },
                    { value: "fivePlus", label: "5명 이상" },
                ]}
            />
            <RadioGroup
                question="여행 구성원의 연령대는 어떻게 되나요?"
                name="ageGroup"
                value={ageGroup}
                onChange={(e) => setAgeGroup(e.target.value)}
                options={[
                    { value: "teens", label: "10대" },
                    { value: "twenties", label: "20대" },
                    { value: "thirties", label: "30대" },
                    { value: "fortyPlus", label: "40대 이상" },
                ]}
            />
            <RadioGroup
                question="여행 기간은 얼마나 되나요?"
                name="duration"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                options={[
                    { value: "oneDay", label: "당일" },
                    { value: "twoDays", label: "2일" },
                    { value: "threeDays", label: "3일" },
                ]}
            />

            <TwoButton
                onPrev={() => navigate(-1)}
                onNext={() => navigate("/course/preference/detail")}
                isNextActive={isNextActive}
            />
        </div>
    );
}