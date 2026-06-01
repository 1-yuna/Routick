import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import PlaceCard from '../../components/place/PlaceCard.jsx';
import PlaceInfoModal from '../../components/place/PlaceInfoModal.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';

// 장소 상세보기 페이지 - mode가 'add'면 장소 추가, 아니면 일반 상세보기
export default function PlaceDetailPage() {
  const [showModal, setShowModal] = useState(false);

  const location = useLocation();
  const mode = location.state?.mode;
  const addPlace = useCourseStore((state) => state.addPlace);
  const navigate = useNavigate();

  const place = location.state;
  if (!place) return null;

  // 머무를 시간 입력 후 코스에 장소 추가
  const handleConfirm = ({ stayTime, category }) => {
    addPlace({ ...place, stayTime, category });
    console.log('category:', place.category);
    navigate('/result');
  };

  return (
    <div className="relative w-full h-screen">
      {/*머무를 시간 입력 모달*/}
      {showModal && (
        <PlaceInfoModal
          onConfirm={handleConfirm}
          onCancel={() => setShowModal(false)}
        />
      )}

      {/*상단 바 - 장소 추가 모드면 TopBar, 아니면 MapTopBar*/}
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
