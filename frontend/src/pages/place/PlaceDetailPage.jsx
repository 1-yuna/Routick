import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import KakaoMap from '../../common/map/KakaoMap.jsx';
import TopBar from '../../common/bar/TopBar.jsx';
import MapTopBar from '../../common/bar/MapTopBar.jsx';
import PlaceCard from '../../components/place/PlaceCard.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import { getTransportTime } from '../../utils/directionUtils.jsx';
import { recalcTransportUtils } from '../../utils/recalcTransportUtils.jsx';
import { minutesToTime } from '../../utils/timeUtils.jsx';
import { getPlaceDetail } from '../../api/place.jsx';

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
  const updateBlocks = useCourseStore((state) => state.updateBlocks);
  const course = useCourseStore((state) => state.course);

  const from = location.state?.from;
  const place = location.state;
  const [placeDetail, setPlaceDetail] = useState(null);

  // lat/lng이 없는 진입(놀거리 카테고리·지역추천 카드 클릭)만 상세조회로 보강
  useEffect(() => {
    if (!place?.placeId || (place.lat != null && place.lng != null)) return;
    (async () => {
      try {
        const res = await getPlaceDetail(place.placeId);
        setPlaceDetail(res.data.data);
      } catch (e) {
        // 실패해도 넘어온 기본 정보로만 표시
      }
    })();
  }, [place?.placeId, place?.lat, place?.lng]);

  const handleBack = () => {
    if (from === 'result') navigate('/result');
    else if (from === 'mytrip') navigate('/mytrip');
    else navigate(-1);
  };
  if (!place) return null;

  const displayPlace = placeDetail
    ? {
        ...place,
        ...placeDetail,
        src: placeDetail.imageUrl ?? place.src ?? null,
      }
    : place;

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
      moveMinutes = await getTransportTime(
        { lat: lastPlace.lat, lng: lastPlace.lng },
        { lat: displayPlace.lat, lng: displayPlace.lng },
        transport === 'car' ? '자동차' : '도보'
      );

      const lastLeaveMinutes = timeToMinutes(lastPlace.leaveTime);
      const arriveMinutes = lastLeaveMinutes + moveMinutes;
      const stayMinutes = DEFAULT_STAY[displayPlace.bucket ?? 'other'];
      arriveTime = minutesToTime(arriveMinutes);
      leaveTime = minutesToTime(arriveMinutes + stayMinutes);
    }

    addPlace(
      {
        ...displayPlace,
        arriveTime,
        leaveTime,
        stayMinutes: DEFAULT_STAY[displayPlace.bucket ?? 'other'],
      },
      dayNumber,
      moveMinutes,
      transport
    );

    // 추가 후 전체 이동시간 재계산
    const updatedDay = useCourseStore
      .getState()
      .course.days.find((d) => d.dayNumber === dayNumber);
    if (updatedDay) {
      const recalculated = await recalcTransportUtils(
        updatedDay.blocks,
        course.transport ?? 'walk'
      );
      const reordered = recalculated.map((block, idx) => ({
        ...block,
        blockOrder: idx + 1,
      }));
      updateBlocks(dayNumber, reordered);
    }

    navigate('/result');
  };

  return (
    <div className="relative w-full h-screen">
      {mode === 'add' ? (
        <div className="absolute top-0 left-0 w-full z-10 pt-12 px-6 bg-white">
          <TopBar
            onClick={handleBack}
            title="장소 추가"
            text="추가"
            className3="text-primary text-16-sb"
            onTextClick={handleAdd}
          >
            <LeftIcon className="w-5 h-10 text-primary" />
          </TopBar>
        </div>
      ) : (
        <MapTopBar onClick={handleBack} />
      )}

      <KakaoMap lat={displayPlace.lat} lng={displayPlace.lng} />
      {displayPlace && <PlaceCard place={displayPlace} />}
    </div>
  );
}
