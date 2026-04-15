import { useNavigate } from "react-router-dom";

import TopBarLogo from "../common/TopBarLogo.jsx";
import BottomBar from "../common/BottomBar.jsx";
import TopCardSection from "../components/home/TopCardSection.jsx";
import HomeBannerCard from "../components/home/HomeBannerCard.jsx";
import home from "../assets/home.png";
import sample from "../assets/sample.png";

export default function HomePage() {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col px-8 pb-40">
            <TopBarLogo/>

            {/*Card*/}
            <HomeBannerCard
                name="윤아"
                image={home}
                onClick={() => navigate("/course/address")}
            />

            {/*Top3*/}
            <TopCardSection
                title="맛집 TOP 3"
                items={[
                    { image: sample, tags: ["홍대", "분위기"]},
                    { image: sample, tags: ["강남", "맛집"] },
                    { image: sample, tags: ["성수", "카페"] },
                ]}
                onClick={() =>console.log("보러갑시다")}
            />

            {/*Top3*/}
            <TopCardSection
                title="카페 TOP 3"
                items={[
                    { image: sample, tags: ["홍대", "분위기"] },
                    { image: sample, tags: ["강남", "맛집"] },
                    { image: sample, tags: ["성수", "카페"] },
                ]}
                onClick={() =>console.log("보러갑시다")}
            />

            <BottomBar/>


        </div>
    );
}