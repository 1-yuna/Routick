import { useNavigate, useSearchParams } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import HotPlaceItem from '../../components/home/PlaceItem.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { mockPlaces } from '../../data/mock/places.jsx';

const TITLE_MAP = {
  hotplace: '핫플',
  exhibition: '전시/문화',
  nature: '자연',
};

// 놀거리 추천 페이지 - type(hotplace/exhibition/nature)에 따라 다른 장소 목록 표시
export default function PlayListPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const type = searchParams.get('type') || 'hotplace';
  const title = TITLE_MAP[type] || '핫플';

  return (
    <div className="px-6 pt-12 flex flex-col h-screen bg-white">
      {/*상단 바*/}
      <TopBar className="bg-white" title={title} onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      {/*장소 목록*/}
      <div className="overflow-y-auto flex flex-col no-scrollbar">
        {mockPlaces.map((place, index) => (
          <HotPlaceItem
            key={place.id}
            place={place}
            index={index + 1}
            onClick={() =>
              navigate(`/place/${place.id}`, { state: { ...place } })
            }
          />
        ))}
      </div>
    </div>
  );
}
