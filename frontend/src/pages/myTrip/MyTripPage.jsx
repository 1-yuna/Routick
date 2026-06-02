import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import EditTripCard from '../../components/myTrip/EditTripCard.jsx';
import TripCard from '../../components/myTrip/TripCard.jsx';
import logo from '../../assets/images/logo.png';
import LeftIcon from '../../assets/icons/left.svg?react';
import useMyTripStore from '../../store/myTripStore.jsx';

// 내 여행 페이지
export default function MyTripPage() {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [checkedTrips, setCheckedTrips] = useState([]);
  const trips = useMyTripStore((state) => state.trips);
  const deleteTrips = useMyTripStore((state) => state.deleteTrips);

  const handleCheck = (id) => {
    setCheckedTrips((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleDelete = () => {
    deleteTrips(checkedTrips);
    setCheckedTrips([]);
  };

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-login relative">
      {/*상단 바*/}
      {isEditing ? (
        <TopBar
          className="px-6 border-b border-line1"
          text="완료"
          className3="text-primary text-16-sb"
          onTextClick={() => {
            setIsEditing(false);
            setCheckedTrips([]);
          }}
          onClick={() => {
            setIsEditing(false);
            setCheckedTrips([]);
          }}
        >
          <LeftIcon className="w-5 h-10 text-primary" />
        </TopBar>
      ) : (
        <TopBar
          className="px-6 border-b border-line1"
          text="편집"
          className3="text-primary text-16-sb"
          onTextClick={() => setIsEditing(true)}
        >
          <img className="w-22 h-11 object-contain" src={logo} />
        </TopBar>
      )}

      {/*여행 목록*/}
      {/*여행 목록*/}
      {trips.length === 0 ? (
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
                key={trip.id}
                trip={trip}
                isChecked={checkedTrips.includes(trip.id)}
                onCheck={() => handleCheck(trip.id)}
              />
            ) : (
              <TripCard
                key={trip.id}
                trip={trip}
                onClick={() =>
                  navigate('/result', { state: { from: 'mytrip' } })
                }
              />
            )
          )}
        </div>
      )}

      {/*삭제 버튼*/}
      {isEditing && checkedTrips.length > 0 && (
        <div className="absolute bottom-0 left-0 w-full px-6 pb-20">
          <FullWidthButton
            text="삭제하기"
            className="bg-primary"
            onClick={handleDelete}
          />
        </div>
      )}

      {!isEditing && <BottomBar />}
    </div>
  );
}
