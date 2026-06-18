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
import { useState } from 'react';
import { REGION_DATA, DEFAULT_REGION } from '../../data/regionData.jsx';
import { mockTopPlaces } from '../../data/mock/topPlaces.jsx';

// 홈 페이지
export default function HomePage() {
  const reset = useCourseStore((state) => state.reset);
  const navigate = useNavigate();
  const [region, setRegion] = useState(DEFAULT_REGION);
  const [showRegionSheet, setShowRegionSheet] = useState(false);

  return (
    <div className="flex flex-col pt-12 pb-32 gap-8 h-screen bg-default">
      {/*지역 설정 바텀시트*/}
      {showRegionSheet && (
        <RegionSelectSheet
          regions={REGION_DATA}
          selected={region}
          onSelect={setRegion}
          onClose={() => setShowRegionSheet(false)}
        />
      )}

      {/*상단 바*/}
      <TopBar className="px-6">
        {/*지역 선택*/}
        <button
          onClick={() => setShowRegionSheet(true)}
          className="flex items-center whitespace-nowrap text-20-sb text-black1"
        >
          {region.category.split(' ')[0]} {region.area}
          <DownIcon className="w-6 h-6 text-black1" />
        </button>
      </TopBar>

      <div className="flex flex-col gap-10 overflow-y-auto no-scrollbar">
        {/*배너*/}
        <CourseBanner
          name="윤아"
          image={home}
          className="px-6"
          onClick={() => {
            reset();
            navigate('/select/address');
          }}
        />

        {/*지역 추천*/}
        <TopCardSection
          name="윤아"
          area={region.area}
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
