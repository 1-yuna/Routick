import { useNavigate } from 'react-router-dom';

import BottomBar from '../../common/bar/BottomBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import TopCardSection from '../../components/home/TopCardSection.jsx';
import CourseBanner from '../../components/home/CourseBanner.jsx';
import PlaySection from '../../components/home/PlaySection.jsx';
import home from '../../assets/images/home.png';
import sample from '../../assets/images/mock/sample.png';
import logo from '../../assets/images/logo.png';
import useCourseStore from '../../store/selectionStore.jsx';
import { useEffect, useState } from 'react';

// TODO: API 연동 시 제거
const mockTopPlaces = [
  {
    id: 1,
    image: sample,
    tags: ['홍대', '데이트 코스'],
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    description: '일본을 대표하는 라멘 전문점',
    lat: 37.5479,
    lng: 126.9228,
    placeId: '1611642967',
  },
  {
    id: 2,
    image: sample,
    tags: ['홍대', '데이트 코스'],
    name: '스타벅스 합정점',
    rating: 4.2,
    reviewCount: 832,
    description: '한강뷰가 보이는 카페',
    lat: 37.5497,
    lng: 126.9143,
    placeId: '1234567890',
  },
  {
    id: 3,
    image: sample,
    tags: ['홍대', '데이트 코스'],
    name: '홍대 놀이터',
    rating: 4.0,
    reviewCount: 512,
    description: '홍대 특유의 활기찬 분위기',
    lat: 37.5564,
    lng: 126.9238,
    placeId: '0987654321',
  },
  {
    id: 4,
    image: sample,
    tags: ['홍대', '데이트 코스'],
    name: '연남동 카페거리',
    rating: 4.5,
    reviewCount: 1023,
    description: '감성적인 카페들이 모여있는 거리',
    lat: 37.5617,
    lng: 126.9237,
    placeId: '1122334455',
  },
  {
    id: 5,
    image: sample,
    tags: ['홍대', '데이트 코스'],
    name: '망원한강공원',
    rating: 4.7,
    reviewCount: 2341,
    description: '한강을 바라보며 쉬어가기 좋은 공원',
    lat: 37.5537,
    lng: 126.9008,
    placeId: '5544332211',
  },
];

// 홈 페이지
export default function HomePage() {
  const navigate = useNavigate();
  const [location, setLocation] = useState(null);
  const reset = useCourseStore((state) => state.reset);

  // 현재 위치 수집
  useEffect(() => {
    console.log('geolocation 시작');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        console.log('현재 위치:', { lat, lng });
        setLocation({ lat, lng });
      },
      (error) => {
        console.error('위치 가져오기 실패:', error.code, error.message);
        // 위치 가져오기 실패 시 서울 기본값
        setLocation({ lat: 37.5665, lng: 126.978 });
      }
    );
  }, []);

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-default">
      {/*상단 바*/}
      <TopBar className="px-6 border-b border-line1">
        <img className="w-22 h-11 object-contain" src={logo} />
      </TopBar>

      <div className="flex flex-col gap-10 overflow-y-auto no-scrollbar">
        {/*배너*/}
        <CourseBanner
          name="윤아"
          image={home}
          className="px-6 pt-8"
          onClick={() => {
            reset();
            navigate('/select/address');
          }}
        />

        {/*Top5*/}
        <TopCardSection
          name="윤아"
          className="pl-6"
          items={mockTopPlaces}
          onClick={(place) =>
            navigate(`/place/${place.id}`, { state: { ...place } })
          }
        />

        {/*놀거리*/}
        <PlaySection
          className="px-6 pt-5 pb-12"
          onHotplace={() => navigate('/playlist?type=hotplace')}
          onExhibition={() => navigate('/playlist?type=exhibition')}
          onNature={() => navigate('/playlist?type=nature')}
        />
      </div>

      {/*하단바*/}
      <BottomBar />
    </div>
  );
}
