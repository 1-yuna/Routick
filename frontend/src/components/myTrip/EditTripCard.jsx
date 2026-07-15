import { useNavigate } from 'react-router-dom';
import CheckIcon from '../../assets/icons/check.svg?react';
import { getImageUrl } from '../../utils/imageUtil.jsx';

// 여행 편집 카드
export default function EditTripCard({ trip, isChecked, onCheck }) {
  const { title, coverImageUrl } = trip;
  const navigate = useNavigate();

  return (
    <div
      className={`flex items-center p-2 gap-2 ${isChecked ? 'bg-button' : 'bg-default'}`}
    >
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-primary border-primary' : 'border-line2'}`}
      >
        {isChecked && <CheckIcon className="text-white w-4 h-4" />}
      </button>

      <div
        className="flex h-[82px] flex-1 bg-white rounded-10 shadow-md cursor-pointer"
        onClick={() => navigate(`/mytrip/edit/${trip.tripId}`, { state: trip })}
      >
        <div className="relative flex-shrink-0">
          <img
            src={getImageUrl(coverImageUrl)}
            alt={title}
            className="w-24 h-full rounded-l-10 object-cover"
          />
          <div className="absolute inset-0 bg-black/45 rounded-l-10" />
        </div>
        <p className="px-3 py-2 text-14-sb text-black1 flex-1">{title}</p>
      </div>
    </div>
  );
}
