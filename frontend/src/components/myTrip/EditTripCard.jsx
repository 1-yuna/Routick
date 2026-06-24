import { useNavigate } from 'react-router-dom';
import CheckIcon from '../../assets/icons/check.svg?react';

// 여행 편집 카드
export default function EditTripCard({ trip, isChecked, onCheck }) {
  const { title, src } = trip;
  const navigate = useNavigate();

  return (
    <div
      className={`flex items-center p-2 gap-2 ${isChecked ? 'bg-button' : 'bg-default'}`}
    >
      {/*체크박스*/}
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-primary border-primary' : 'border-line2'}`}
      >
        {isChecked && <CheckIcon className="text-white w-4 h-4" />}
      </button>

      {/*카드*/}
      <div
        className="flex h-[82px] flex-1 bg-white rounded-10 shadow-md cursor-pointer"
        onClick={() => navigate(`/mytrip/edit/${trip.id}`, { state: trip })}
      >
        <div className="relative flex-shrink-0">
          <img
            src={src}
            alt={title}
            className="w-24 h-full rounded-l-10 object-cover"
          />
          <div className="absolute inset-0 bg-black/45 rounded-l-10" />
        </div>
        {/*제목*/}
        <p className="px-3 py-2 text-14-sb text-black1 flex-1">{title}</p>
      </div>
    </div>
  );
}
