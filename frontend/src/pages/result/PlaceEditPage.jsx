import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import CameraIcon from '../../assets/icons/camera.svg?react';
import DownIcon from '../../assets/icons/down.svg?react';
import useCourseStore from '../../store/courseStore.jsx';
import PlaceImageDefault from '../../common/imageDefault/PlaceImageDefault.jsx';

const BUCKET_OPTIONS = [
  { value: 'food', label: '음식' },
  { value: 'cafe', label: '카페' },
  { value: 'activity', label: '활동' },
  { value: 'parking', label: '주차장' },
  { value: 'other', label: '기타' },
];

const STATUS_OPTIONS = [
  { value: '영업 중', label: '영업 중' },
  { value: '브레이크 타임', label: '브레이크 타임' },
  { value: '휴무', label: '휴무' },
];

const STAY_OPTIONS = [
  { value: 30, label: '30분' },
  { value: 60, label: '1시간' },
  { value: 90, label: '1시간 30분' },
  { value: 120, label: '2시간' },
  { value: 150, label: '2시간 30분' },
  { value: 180, label: '3시간' },
  { value: 210, label: '3시간 30분' },
  { value: 240, label: '4시간' },
];

export default function PlaceEditPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const updatePlace = useCourseStore((state) => state.updatePlace);
  const updateParking = useCourseStore((state) => state.updateParking);

  const block = location.state;
  const isParking = block?.type === 'parking';

  const [name, setName] = useState(block?.name ?? '');
  const [bucket, setBucket] = useState(
    block?.bucket ?? (isParking ? 'parking' : 'other')
  );
  const [status, setStatus] = useState(
    block?.status ?? (isParking ? '' : '영업 중')
  );
  const [stayMinutes, setStayMinutes] = useState(
    block?.stayMinutes ?? (isParking ? '' : 90)
  );
  const [description, setDescription] = useState(block?.description ?? '');
  const [fee, setFee] = useState(block?.fee ?? '');
  const [src, setSrc] = useState(block?.src ?? null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setSrc(ev.target.result);
    reader.readAsDataURL(file);
  };

  if (!block) return null;

  const isBlockingParking = bucket === 'parking';

  const goBack = () => navigate('/result', { state: { isEditing: true } });

  const handleDone = () => {
    if (bucket === 'parking') {
      updateParking(block.name ?? block.placeId, block.dayNumber, {
        name,
        description,
      });
    } else {
      updatePlace(block.placeId ?? block.name, block.dayNumber, {
        name,
        bucket,
        status,
        stayMinutes,
        description,
        src,
      });
    }
    goBack();
  };

  return (
    <div className="w-full min-h-screen bg-white flex flex-col">
      <div className="pt-12 px-6">
        <TopBar
          onClick={goBack}
          title="장소 편집"
          text="완료"
          className3="text-primary text-16-sb"
          onTextClick={handleDone}
        >
          <LeftIcon className="w-5 h-10 text-primary" />
        </TopBar>
      </div>

      <div className="flex flex-col gap-[28px] px-6 pt-6 pb-10">
        {/* 이미지 + 이름 */}
        <div className="flex items-center gap-3">
          <label className="relative w-24 h-24 flex-shrink-0 cursor-pointer">
            {src ? (
              <img
                src={src}
                alt="장소 이미지"
                className="w-24 h-24 object-cover rounded-5"
              />
            ) : (
              <PlaceImageDefault className="w-24 h-24 rounded-5" />
            )}
            <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-5">
              <CameraIcon className="w-6 h-6 text-white" />
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />
          </label>
          <div className="flex flex-col gap-2 flex-1">
            <p className="text-14-sb text-black1">가게 이름</p>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={block.name}
              className="w-full rounded-5 px-3 py-2 text-14-rg text-gray2 bg-neutral outline-none"
            />
          </div>
        </div>

        {/* 유형 */}
        <div className="flex flex-col gap-2">
          <p className="text-14-sb text-black1">유형</p>
          <div className="flex gap-3 flex-wrap">
            {BUCKET_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setBucket(opt.value)}
                className={`px-3 py-2 rounded-full text-12-rg ${
                  bucket === opt.value
                    ? 'bg-primary text-white'
                    : 'bg-neutral text-black1'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* 영업 상태 - parking이면 비활성화 */}
        <div
          className={`flex flex-col gap-2 ${isBlockingParking ? 'opacity-30' : ''}`}
        >
          <p className="text-14-sb text-black1">영업 상태</p>
          <div className="flex gap-3 flex-wrap">
            {STATUS_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => !isBlockingParking && setStatus(opt.value)}
                className={`px-3 py-2 rounded-full text-12-rg ${
                  status === opt.value
                    ? 'bg-primary text-white'
                    : 'bg-neutral text-black1'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* 머무를 시간 - parking이면 비활성화 */}
        <div
          className={`flex flex-col gap-2 ${isBlockingParking ? 'opacity-30' : ''}`}
        >
          <p className="text-14-sb text-black1">머무를 시간</p>
          <div className="relative">
            <select
              value={stayMinutes}
              onChange={(e) => setStayMinutes(Number(e.target.value))}
              disabled={isBlockingParking}
              className="w-full bg-neutral rounded-5 px-3 py-2 text-12-rg text-black1 outline-none appearance-none"
            >
              {isBlockingParking && <option value="">-</option>}
              {STAY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <DownIcon className="w-5 h-5 absolute right-3 top-1/2 -translate-y-1/2 text-black1 pointer-events-none" />
          </div>
        </div>

        {/* 한줄 소개 */}
        <div className="flex flex-col gap-2">
          <p className="text-14-sb text-black1">한줄 소개</p>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full bg-neutral rounded-5 px-3 py-2 text-12-rg text-black1 outline-none resize-none"
          />
        </div>
      </div>
    </div>
  );
}
