import { useNavigate, useSearchParams } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import HotPlaceItem from '../../components/home/PlaceItem.jsx';
import SampleImage from '../../assets/images/mock/sample.png';

const mockPlaces = [
  {
    id: 1,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 2,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 3,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 4,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 5,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 6,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
  {
    id: 7,
    name: '타코잇 상수역점',
    rating: 4.6,
    reviewCount: 1243,
    address: '경기 고양시 덕양구 동산동 370',
    src: SampleImage,
  },
];

const TITLE_MAP = {
  hotplace: '핫플',
  exhibition: '전시/문화',
  nature: '자연',
};

// 놀거리 추천 페이지
export default function PlayListPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const type = searchParams.get('type') || 'hotplace';
  const title = TITLE_MAP[type] || '핫플';

  return (
    <div className="px-6 pt-12 flex flex-col h-screen bg-white">
      <TopBar
        className="bg-white border-b border-line1"
        title={title}
        onClick={() => navigate(-1)}
      >
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="overflow-y-auto flex flex-col gap-6 py-6 no-scrollbar">
        {mockPlaces.map((place, index) => (
          <HotPlaceItem
            key={place.id}
            place={place}
            index={index + 1}
            onClick={() => navigate(`/place/${place.id}`)}
          />
        ))}
      </div>
    </div>
  );
}
