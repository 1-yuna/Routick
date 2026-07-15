import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import HotPlaceItem from '../../components/home/PlaceItem.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { getCachedPlaceList } from '../../utils/placeListCache.jsx';
import { getImageUrl } from '../../utils/imageUtil.jsx';

const TITLE_MAP = {
  hotplace: '핫플',
  'culture-nature': '문화/자연',
  'food-cafe': '맛집/카페',
};

const CATEGORY_MAP = {
  hotplace: 'HOTPLACE',
  'culture-nature': 'CULTURE_NATURE',
  'food-cafe': 'FOOD_CAFE',
};

// type별 스크롤 위치 (모듈 레벨, 언마운트돼도 유지)
const scrollPositions = {};

export default function PlayListPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const type = searchParams.get('type') || 'hotplace';
  const title = TITLE_MAP[type] || '핫플';
  const category = CATEGORY_MAP[type] || 'HOTPLACE';
  const regionName = searchParams.get('regionName');
  const lat = Number(searchParams.get('lat'));
  const lng = Number(searchParams.get('lng'));

  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!regionName || !lat || !lng) return;
    getCachedPlaceList(category, regionName, lat, lng)
      .then((items) => {
        setPlaces(
          items.map((item) => ({
            placeId: item.placeId,
            name: item.name,
            longDescription: item.longDescription,
            address: item.address,
            src: getImageUrl(item.imageUrl),
          }))
        );
      })
      .catch(() => setPlaces([]))
      .finally(() => setLoading(false));
  }, [category, regionName, lat, lng]);
  // 실제 목록이 렌더된 뒤(로딩 끝난 뒤) 이전 스크롤 위치 복원
  useEffect(() => {
    if (!loading && scrollRef.current) {
      scrollRef.current.scrollTop = scrollPositions[type] ?? 0;
    }
  }, [loading, type]);

  const handleScroll = (e) => {
    scrollPositions[type] = e.currentTarget.scrollTop;
  };

  return (
    <div className="px-6 pt-12 flex flex-col h-screen bg-white">
      <TopBar className="bg-white" title={title} onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="overflow-y-auto flex flex-col no-scrollbar"
      >
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-4 py-4 border-b border-line1">
                <div className="w-28 h-28 rounded-5 bg-neutral animate-pulse shrink-0" />
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-line2 animate-bounce" />
                </div>
              </div>
            ))
          : places.map((place, index) => (
              <HotPlaceItem
                key={place.placeId}
                place={place}
                index={index + 1}
                onClick={() =>
                  navigate(`/place/${place.placeId}`, {
                    state: { ...place },
                  })
                }
              />
            ))}
      </div>
    </div>
  );
}
