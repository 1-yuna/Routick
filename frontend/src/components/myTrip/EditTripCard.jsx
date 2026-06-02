import CameraIcon from '../../assets/icons/camera.svg?react';

// 여행 편집 카드
export default function EditTripCard({ trip, isChecked, onCheck }) {
  const { title, src } = trip;

  return (
    <div
      className={`flex items-center p-2 gap-3 ${isChecked ? 'bg-line1' : 'bg-login'}`}
    >
      {/*체크박스*/}
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-primary border-primary' : 'border-line2'}`}
      >
        {isChecked && <span className="text-white text-10-sb">✓</span>}
      </button>

      {/*카드*/}
      <div className="flex h-[82px] flex-1 bg-white rounded-[10px] shadow-[3px_3px_10px_rgba(0,0,0,0.1)]">
        <div className="relative flex-shrink-0">
          <img
            src={src}
            alt={title}
            className="w-[116px] h-full rounded-l-[10px] object-cover"
          />
          {/*어두운 오버레이*/}
          <div className="absolute inset-0 bg-black/35 rounded-l-[10px]" />
          {/*카메라 아이콘*/}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-1">
            <CameraIcon className="w-6 h-6 text-white" />
            <span className="text-10-rg text-white">커버</span>
          </div>
        </div>
        <p className="p-3 text-14-sb text-black1">{title}</p>
      </div>
    </div>
  );
}
