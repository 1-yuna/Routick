import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { useLocation, useNavigate } from 'react-router-dom';
import PlaceCard from '../../components/place/PlaceCard.jsx';
import { useState } from 'react';
import SampleImage from '../../assets/images/mock/sample.png';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import useCourseStore from '../../store/courseStore.jsx';
import TimeInputModal from '../../components/place/TimeInputModal.jsx';

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
  const [showModal, setShowModal] = useState(false);

  // 현재 페이지 정보 가져오기
  const location = useLocation();
  const mode = location.state?.mode;
  const addPlace = useCourseStore((state) => state.addPlace);

  const navigate = useNavigate();
  const [place] = useState(mode === 'add' ? location.state : mockPlace);

  const handleConfirm = (stayTime) => {
    addPlace({ ...place, stayTime });
    navigate('/result');
  };

  return (
    <div className="relative w-full h-screen">
      {showModal && (
        <TimeInputModal
          onConfirm={handleConfirm}
          onCancel={() => setShowModal(false)}
        />
      )}

      {/* mode가 'add'면 TopBar, 아니면 MapTopBar*/}
      {mode === 'add' ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={() => navigate(-1)}
            title="장소 추가"
            text="추가"
            className3="text-primary text-16-sb"
            onTextClick={() => setShowModal(true)}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar onClick={() => navigate(-1)} />
      )}

      {/*지도*/}
      <KakaoMap lat={place.lat} lng={place.lng} />

      {/*하단 카드*/}
      {place && <PlaceCard place={place} />}
    </div>
  );
}
