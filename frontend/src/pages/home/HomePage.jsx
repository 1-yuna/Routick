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
import { useState } from 'react';
import { REGION_DATA, DEFAULT_REGION } from '../../data/regionData.jsx';
import { mockTopPlaces } from '../../data/mock/topPlaces.jsx';
import { updateLocation } from '../../api/user.jsx';

// REGION_DATA에서 regionName으로 {category, area} 찾기 (lastLocation 복원용)
const findRegionByName = (regionName) => {
  for (const cat of REGION_DATA) {
    const area = cat.areas.find((a) => a.name === regionName);
    if (area) return { category: cat.category, area };
  }
  return null;
};

// 홈 페이지
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

  // 지역 선택 - 화면 반영 + 서버에 마지막 위치 저장
  const handleSelectRegion = (newRegion) => {
    setRegion(newRegion);
    updateLocation(
      newRegion.area.name,
      newRegion.area.lat,
      newRegion.area.lng
    ).catch(() => {});
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

      <div className="flex flex-col gap-10 overflow-y-auto no-scrollbar">
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
          items={mockTopPlaces}
        />

        <PlaySection
          className="px-6 pt-5 pb-12"
          onHotplace={() => navigate('/playlist?type=hotplace')}
          onCultureNature={() => navigate('/playlist?type=culture-nature')}
          onFoodCafe={() => navigate('/playlist?type=food-cafe')}
        />
      </div>

      <BottomBar />
    </div>
  );
}
