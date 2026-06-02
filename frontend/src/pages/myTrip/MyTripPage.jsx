import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import SampleImage from '../../assets/images/mock/sample.png';
import logo from '../../assets/images/logo.png';
import TripCard from '../../components/myTrip/TripCard.jsx';

const mockTrips = [
  {
    id: 1,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑', '즐겁다'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 2,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '배고프다다'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 3,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 4,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
  {
    id: 5,
    title: '자녀와 함께하는 봄여행',
    address: '홍대역 2번출구',
    transport: '도보',
    tags: ['깔끔한', '자연/산책', '쇼핑'],
    hashtags: ['혼자', '당일치기'],
    src: SampleImage,
  },
];

// 내 여행 페이지
export default function MyTripPage() {
  const navigate = useNavigate();

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-login">
      {/*상단 바*/}
      <TopBar
        className="px-6 border-b border-line1"
        text="편집"
        className3="text-primary text-16-sb"
        onTextClick={() => console.log('편집')}
      >
        {' '}
        <img className="w-22 h-11 object-contain" src={logo} />
      </TopBar>

      {/*여행 목록*/}
      <div className="overflow-y-auto no-scrollbar flex flex-col gap-4 px-6 py-4">
        {mockTrips.map((trip) => (
          <TripCard
            key={trip.id}
            trip={trip}
            onClick={() => navigate('/result', { state: { from: 'mytrip' } })}
          />
        ))}
      </div>

      {/*하단 바*/}
      <BottomBar />
    </div>
  );
}
