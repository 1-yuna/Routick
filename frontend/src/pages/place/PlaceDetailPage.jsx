import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { useNavigate } from 'react-router-dom';
import PlaceCard from '../../components/place/PlaceCard.jsx';

// 상세보기 페이지
export default function PlaceDetailPage() {
  const navigate = useNavigate();

  return (
    <div className="py-12 relative w-full h-screen">
      {/*상단 바*/}
      <TopBar className="px-6 bg-white" onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      {/*지도*/}
      <KakaoMap />

      {/*하단 카드*/}
      <PlaceCard
        name="타코잇 상수역점"
        rating="4.6"
        reviewCount="1,243"
        description="일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음"
      />
    </div>
  );
}
