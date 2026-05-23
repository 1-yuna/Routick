import { useNavigate } from 'react-router-dom';

import BottomBar from '../../common/bar/BottomBar.jsx';
import TopCardSection from '../../components/home/TopCardSection.jsx';
import CourseBanner from '../../components/home/CourseBanner.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import PlaySection from '../../components/home/PlaySection.jsx';
import home from '../../assets/images/home.png';
import sample from '../../assets/images/mock/sample.png';
import logo from '../../assets/images/logo.png';
import useCourseStore from '../../store/selectionStore.jsx';

// 홈 페이지
export default function HomePage() {
  const navigate = useNavigate();
  const reset = useCourseStore((state) => state.reset);

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-default">
      {/*상단 바*/}
      <TopBar
        className="px-6 bg-white border-b border-line1"
        onClick={() => navigate('/home')}
      >
        <img className="w-22 h-11 object-contain" src={logo} />
      </TopBar>

      <div className="flex flex-col gap-10 overflow-y-auto no-scrollbar">
        {/*Card*/}
        <CourseBanner
          name="윤아"
          image={home}
          className="px-6 pt-8 "
          onClick={() => {
            reset();
            navigate('/select/address');
          }}
        />

        {/*Top5*/}
        <TopCardSection
          name="윤아"
          className="pl-6"
          items={[
            { image: sample, tags: ['홍대', '데이트 코스'] },
            { image: sample, tags: ['홍대', '데이트 코스'] },
            { image: sample, tags: ['홍대', '데이트 코스'] },
            { image: sample, tags: ['홍대', '데이트 코스'] },
            { image: sample, tags: ['홍대', '데이트 코스'] },
          ]}
          onClick={() => navigate('/place/1')}
        />

        {/*놀거리*/}
        <PlaySection
          className="px-6 pt-5 pb-12"
          onClick={() => console.log('놀거리')}
        />
      </div>

      {/*하단바*/}
      <BottomBar />
    </div>
  );
}
