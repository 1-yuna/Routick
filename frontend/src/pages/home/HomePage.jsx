import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import BottomBar from '../../common/bar/BottomBar.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import TopCardSection from '../../components/home/TopCardSection.jsx';
import CourseBanner from '../../components/home/CourseBanner.jsx';
import PlaySection from '../../components/home/PlaySection.jsx';
import RegionSelectSheet from '../../components/home/RegionSelectSheet.jsx';
import home from '../../assets/images/home.png';
import DownIcon from '../../assets/icons/down.svg?react';
import useCourseStore from '../../store/selectionStore.jsx';
import useUserStore from '../../store/userStore.jsx';
import { REGION_DATA, DEFAULT_REGION } from '../../data/regionData.jsx';
import { updateLocation } from '../../api/user.jsx';
import { getRecommendations } from '../../api/place.jsx';
import { getImageUrl } from '../../utils/imageUtil.jsx';

const findRegionByName = (regionName) => {
  for (const cat of REGION_DATA) {
    const area = cat.areas.find((a) => a.name === regionName);
    if (area) return { category: cat.category, area };
  }
  return null;
};

// 컴포넌트가 언마운트돼도 유지되는 스크롤 위치 (모듈 레벨)
let homeScrollTop = 0;

export default function HomePage() {
  const reset = useCourseStore((state) => state.reset);
  const user = useUserStore((state) => state.user);
  const navigate = useNavigate();
  const [region, setRegion] = useState(() => {
    const location = user?.lastLocation;
    if (location) {
      const found = findRegionByName(location.regionName);
      if (found) return found;
    }
    return DEFAULT_REGION;
  });
  const [showRegionSheet, setShowRegionSheet] = useState(false);
  const [topPlaces, setTopPlaces] = useState([]);
  const [loadingTopPlaces, setLoadingTopPlaces] = useState(true);
  const updateUser = useUserStore((state) => state.updateUser);
  const scrollRef = useRef(null);

  // 마운트 시 이전 스크롤 위치 복원
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = homeScrollTop;
    }
  }, []);

  const handleScroll = (e) => {
    homeScrollTop = e.currentTarget.scrollTop;
  };

  const navigateToPlaylist = (type) => {
    const params = new URLSearchParams({
      type,
      regionName: region.area.name,
      lat: region.area.lat,
      lng: region.area.lng,
    });
    navigate(`/playlist?${params.toString()}`);
  };

  // 지역 바뀔 때마다 지역추천 TOP5 재조회
  useEffect(() => {
    setLoadingTopPlaces(true);
    (async () => {
      try {
        const res = await getRecommendations(
          region.area.name,
          region.area.lat,
          region.area.lng
        );
        const items = res.data.data.items.map((item) => ({
          src: getImageUrl(item.imageUrl),
          name: item.title,
          tags: item.tags,
          placeId: item.placeId,
          lat: item.lat,
          lng: item.lng,
        }));
        setTopPlaces(items);
      } catch (e) {
        setTopPlaces([]);
      } finally {
        setLoadingTopPlaces(false);
      }
    })();
  }, [region.area.name, region.area.lat, region.area.lng]);

  const handleSelectRegion = (newRegion) => {
    setRegion(newRegion);
    updateUser({
      lastLocation: {
        regionName: newRegion.area.name,
        lat: newRegion.area.lat,
        lng: newRegion.area.lng,
      },
    });
    updateLocation(
      newRegion.area.name,
      newRegion.area.lat,
      newRegion.area.lng
    ).catch(() => {});
  };

  const handleTopPlaceClick = (item) => {
    if (!item.placeId) return;
    navigate(`/place/${item.placeId}`, {
      state: {
        placeId: item.placeId,
        name: item.name,
        src: item.src,
        lat: item.lat,
        lng: item.lng,
        from: 'home',
      },
    });
  };

  return (
    <div className="flex flex-col pt-12 pb-32 gap-8 h-screen bg-default">
      {showRegionSheet && (
        <RegionSelectSheet
          regions={REGION_DATA}
          selected={region}
          onSelect={handleSelectRegion}
          onClose={() => setShowRegionSheet(false)}
        />
      )}

      <TopBar
        className="px-6"
        leftContent={
          <button
            onClick={() => setShowRegionSheet(true)}
            className="flex items-center whitespace-nowrap text-20-sb text-black1"
          >
            {region.category.split(' ')[0]} {region.area.name}
            <DownIcon className="w-6 h-6 text-black1" />
          </button>
        }
      />

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex flex-col gap-10 overflow-y-auto no-scrollbar"
      >
        <CourseBanner
          name={user?.nickname}
          image={home}
          className="px-6"
          onClick={() => {
            reset();
            navigate('/select/period');
          }}
        />

        <TopCardSection
          name={user?.nickname}
          area={region.area.name}
          className="pl-6"
          items={topPlaces}
          loading={loadingTopPlaces}
          onClick={handleTopPlaceClick}
        />

        <PlaySection
          className="px-6 pt-5 pb-12"
          onHotplace={() => navigateToPlaylist('hotplace')}
          onCultureNature={() => navigateToPlaylist('culture-nature')}
          onFoodCafe={() => navigateToPlaylist('food-cafe')}
        />
      </div>

      <BottomBar />
    </div>
  );
}
