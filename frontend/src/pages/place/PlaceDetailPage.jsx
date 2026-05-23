import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { useNavigate } from 'react-router-dom';
import PlaceCard from '../../components/place/PlaceCard.jsx';
import { useState } from 'react';
import SampleImage from '../../assets/images/mock/sample.png';
import MapTopBar from '../../common/bar/MapTopBar.jsx';

const mockPlace = {
  id: 1,
  name: '타코잇 상수역점',
  rating: 4.6,
  reviewCount: 1243,
  description: '일본을 대표하는 라멘 전문점으로 연인과 방문하기에 좋음',
  lat: 37.5479,
  lng: 126.9228,
  placeId: '1611642967',
  src: SampleImage,
};

// 상세보기 페이지
export default function PlaceDetailPage() {
  const navigate = useNavigate();
  const [place, setPlace] = useState(mockPlace);

  return (
    <div className="relative w-full h-screen">
      {/*상단 바*/}
      <MapTopBar onClick={() => navigate(-1)} />

      {/*지도*/}
      <KakaoMap lat={place.lat} lng={place.lng} />

      {/*하단 카드*/}
      {place && <PlaceCard place={place} />}
    </div>
  );
}
