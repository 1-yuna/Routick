import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import HotPlaceItem from '../../components/home/PlaceItem.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import { getPlaceList } from '../../api/place.jsx';
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

// 놀거리 추천 페이지 - type(hotplace/culture-nature/food-cafe)에 따라 다른 장소 목록 표시
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

  useEffect(() => {
    if (!regionName || !lat || !lng) return;
    setLoading(true);
    (async () => {
      try {
        const res = await getPlaceList(category, regionName, lat, lng);
        const items = res.data.data.items.map((item) => ({
          placeId: item.placeId,
          name: item.name,
          longDescription: item.longDescription,
          address: item.address,
          src: getImageUrl(item.imageUrl),
        }));
        setPlaces(items);
      } catch (e) {
        setPlaces([]);
      } finally {
        setLoading(false);
      }
    })();
  }, [category, regionName, lat, lng]);

  return (
    <div className="px-6 pt-12 flex flex-col h-screen bg-white">
      {/*상단 바*/}
      <TopBar className="bg-white" title={title} onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      {/*장소 목록*/}
      <div className="overflow-y-auto flex flex-col no-scrollbar">
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
