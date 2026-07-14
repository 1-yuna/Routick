import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import EditTripCard from '../../components/myTrip/EditTripCard.jsx';
import TripCard from '../../components/myTrip/TripCard.jsx';
import BaseModal from '../../common/modal/BaseModal.jsx';
import logo from '../../assets/images/logo.png';
import LeftIcon from '../../assets/icons/left.svg?react';
import useMyTripStore from '../../store/myTripStore.jsx';
import useCourseStore from '../../store/courseStore.jsx';
import { getTrips, getTripDetail, deleteTrip } from '../../api/trip.jsx';
import { normalizeCourse } from '../../utils/courseUtils.jsx';

export default function MyTripPage() {
  const trips = useMyTripStore((state) => state.trips);
  const setTrips = useMyTripStore((state) => state.setTrips);
  const deleteTrips = useMyTripStore((state) => state.deleteTrips);
  const setCourse = useCourseStore((state) => state.setCourse);
  const navigate = useNavigate();
  const location = useLocation();
  const [isEditing, setIsEditing] = useState(
    location.state?.isEditing ?? false
  );
  const [loading, setLoading] = useState(true);

  if (location.state?.isEditing) {
    window.history.replaceState({}, '');
  }
  const [checkedTrips, setCheckedTrips] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await getTrips();
        setTrips(res.data.data.trips);
      } catch (e) {
        setTrips([]); // 실패 시 명시적으로 비움
      } finally {
        setLoading(false);
      }
    })();
  }, [setTrips]);

  const handleCheck = (id) => {
    setCheckedTrips((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleDelete = async () => {
    try {
      await Promise.all(checkedTrips.map((id) => deleteTrip(id)));
      deleteTrips(checkedTrips);
    } catch (e) {
      alert('삭제에 실패했어요. 다시 시도해주세요.');
    } finally {
      setCheckedTrips([]);
      setShowDeleteModal(false);
    }
  };

  const handleTripClick = async (trip) => {
    try {
      const res = await getTripDetail(trip.tripId);
      setCourse(normalizeCourse(res.data.data));
      navigate('/result', { state: { from: 'mytrip' } });
    } catch (e) {
      alert('여행 정보를 불러오지 못했어요.');
    }
  };

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-default relative">
      {isEditing ? (
        <TopBar
          className="px-6"
          className3="text-primary text-16-sb"
          onClick={() => {
            setIsEditing(false);
            setCheckedTrips([]);
          }}
        >
          <LeftIcon className="w-5 h-10 text-primary" />
        </TopBar>
      ) : (
        <TopBar
          className="px-6"
          text="편집"
          className3="text-primary text-16-sb"
          onTextClick={() => setIsEditing(true)}
        >
          <img className="w-22 h-11 object-contain" src={logo} />
        </TopBar>
      )}

      {!loading && trips.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-14-rg text-gray2">아직 저장된 여행이 없어요 🥲</p>
        </div>
      ) : (
        <div
          className={`overflow-y-auto no-scrollbar flex flex-col px-6 py-4 flex-1 ${isEditing ? '' : 'gap-4'}`}
        >
          {trips.map((trip) =>
            isEditing ? (
              <EditTripCard
                key={trip.tripId}
                trip={trip}
                isChecked={checkedTrips.includes(trip.tripId)}
                onCheck={() => handleCheck(trip.tripId)}
              />
            ) : (
              <TripCard
                key={trip.tripId}
                trip={trip}
                onClick={() => handleTripClick(trip)}
              />
            )
          )}
        </div>
      )}

      {showDeleteModal && (
        <BaseModal
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
        >
          <p className="text-14-sb text-black1">이 여행을 삭제하시겠습니까?</p>
          <p className="text-12-rg text-gray2">
            내 여행 목록에서 바로 삭제돼요.
          </p>
        </BaseModal>
      )}

      {isEditing && checkedTrips.length > 0 && (
        <div className="absolute bottom-0 left-0 w-full px-6 pb-[88px]">
          <FullWidthButton
            text="삭제하기"
            className="bg-primary"
            onClick={() => setShowDeleteModal(true)}
          />
        </div>
      )}

      {!isEditing && <BottomBar />}
    </div>
  );
}
