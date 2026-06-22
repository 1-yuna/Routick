import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
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
  const [bucket, setBucket] = useState(block?.bucket ?? 'other');
  const [status, setStatus] = useState(block?.status ?? '영업 중');
  const [stayMinutes, setStayMinutes] = useState(block?.stayMinutes ?? 60);
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

  const goBack = () => navigate('/result', { state: { isEditing: true } });

  const handleDone = () => {
    if (isParking) {
      updateParking(block.name, block.dayNumber, { name, fee });
    } else {
      updatePlace(block.placeId, block.dayNumber, {
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

      <div className="flex flex-col gap-6 px-6 pt-6 pb-10">
        {/* 이미지 + 이름 */}
        <div className="flex items-center gap-4">
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
              <span className="text-white text-20">📷</span>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />
          </label>
          <div className="flex flex-col gap-1 flex-1">
            <p className="text-12-rg text-gray2">이름</p>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={block.name}
              className="w-full border border-line1 rounded-5 px-3 py-2 text-14-rg text-black1 outline-none"
            />
          </div>
        </div>

        {isParking ? (
          <div className="flex flex-col gap-3">
            <p className="text-16-sb text-black1">요금</p>
            <input
              value={fee}
              onChange={(e) => setFee(e.target.value)}
              placeholder="예: 30분에 500원"
              className="w-full border border-line1 rounded-5 px-3 py-3 text-14-rg text-black1 outline-none"
            />
          </div>
        ) : (
          <>
            <div className="flex flex-col gap-3">
              <p className="text-16-sb text-black1">유형</p>
              <div className="flex gap-2 flex-wrap">
                {BUCKET_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setBucket(opt.value)}
                    className={`px-4 py-2 rounded-full text-14-rg border ${
                      bucket === opt.value
                        ? 'bg-primary text-white border-primary'
                        : 'bg-white text-gray2 border-line1'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <p className="text-16-sb text-black1">영업 상태</p>
              <div className="flex gap-2 flex-wrap">
                {STATUS_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setStatus(opt.value)}
                    className={`px-4 py-2 rounded-full text-14-rg border ${
                      status === opt.value
                        ? 'bg-primary text-white border-primary'
                        : 'bg-white text-gray2 border-line1'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <p className="text-16-sb text-black1">머무를 시간</p>
              <div className="relative">
                <select
                  value={stayMinutes}
                  onChange={(e) => setStayMinutes(Number(e.target.value))}
                  className="w-full border border-line1 rounded-5 px-3 py-3 text-14-rg text-black1 outline-none appearance-none bg-white"
                >
                  {STAY_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray2 pointer-events-none">
                  ▼
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <p className="text-16-sb text-black1">한줄 소개</p>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="w-full border border-line1 rounded-5 px-3 py-3 text-14-rg text-black1 outline-none resize-none"
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
