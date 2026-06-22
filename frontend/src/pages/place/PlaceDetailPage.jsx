import { useLocation, useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import PlaceCard from '../../components/place/PlaceCard.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import { getTransportTime } from '../../utils/directionUtils.jsx';
import { minutesToTime } from '../../utils/timeUtils.jsx';

// HH:MM → 분 변환
function timeToMinutes(time) {
  if (!time) return 0;
  const [h, m] = time.split(':').map(Number);
  return h * 60 + m;
}

// bucket별 기본 체류시간
const DEFAULT_STAY = {
  cafe: 90,
  food: 90,
  activity: 120,
  other: 90,
};

export default function PlaceDetailPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const mode = location.state?.mode;
  const dayNumber = location.state?.dayNumber ?? 1;
  const addPlace = useCourseStore((state) => state.addPlace);
  const course = useCourseStore((state) => state.course);

  const place = location.state;
  if (!place) return null;

  // course.transport 기준 ('car' | 'walk')
  const transport = course.transport ?? 'walk';

  const handleAdd = async () => {
    const dayData = course.days.find((d) => d.dayNumber === dayNumber);
    const blocks = dayData?.blocks ?? [];
    const lastPlace = [...blocks].reverse().find((b) => b.type === 'place');

    let moveMinutes = 10;
    let arriveTime = '';
    let leaveTime = '';

    if (lastPlace) {
      // transport에 따라 이동시간 계산
      moveMinutes = await getTransportTime(
        { lat: lastPlace.lat, lng: lastPlace.lng },
        { lat: place.lat, lng: place.lng },
        transport === 'car' ? '자동차' : '도보'
      );

      const lastLeaveMinutes = timeToMinutes(lastPlace.leaveTime);
      const arriveMinutes = lastLeaveMinutes + moveMinutes;
      const stayMinutes = DEFAULT_STAY[place.bucket ?? 'other'];
      arriveTime = minutesToTime(arriveMinutes);
      leaveTime = minutesToTime(arriveMinutes + stayMinutes);
    }

    addPlace(
      {
        ...place,
        arriveTime,
        leaveTime,
        stayMinutes: DEFAULT_STAY[place.bucket ?? 'other'],
      },
      dayNumber,
      moveMinutes,
      transport // 'car' | 'walk' - walk 블록 타입 결정용
    );

    navigate('/result');
  };

  return (
    <div className="relative w-full h-screen">
      {mode === 'add' ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={() => navigate(-1)}
            title="장소 추가"
            text="추가"
            className3="text-primary text-16-sb"
            onTextClick={handleAdd}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar onClick={() => navigate(-1)} />
      )}

      <KakaoMap lat={place.lat} lng={place.lng} />
      {place && <PlaceCard place={place} />}
    </div>
  );
}
