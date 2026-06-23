import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import CameraIcon from '../../assets/icons/camera.svg?react';
import BaseModal from '../../common/modal/BaseModal.jsx';
import useMyTripStore from '../../store/myTripStore.jsx';

export default function MyTripEditPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const trip = location.state;

  const updateTripTitle = useMyTripStore((state) => state.updateTripTitle);
  const updateTripImage = useMyTripStore((state) => state.updateTripImage);

  const [title, setTitle] = useState(trip?.title ?? '');
  const [src, setSrc] = useState(trip?.src ?? null);
  const [showSaveModal, setShowSaveModal] = useState(false);

  if (!trip) return null;

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const imageUrl = URL.createObjectURL(file);
    setSrc(imageUrl);
  };

  const handleSave = () => {
    updateTripTitle(trip.id, title);
    updateTripImage(trip.id, src);
    setShowSaveModal(false);
    navigate('/mytrip', { state: { isEditing: true } });
  };

  return (
    <div className="w-full min-h-screen bg-white flex flex-col">
      {showSaveModal && (
        <BaseModal
          onConfirm={handleSave}
          onCancel={() => setShowSaveModal(false)}
        >
          <p className="text-14-sb text-black1">저장하시겠습니까?</p>
          <p className="text-12-rg text-gray2">변경된 내용이 저장돼요.</p>
        </BaseModal>
      )}

      <div className="pt-12 px-6">
        <TopBar
          onClick={() => navigate(-1)}
          title="여행 편집"
          text="완료"
          className3="text-primary text-16-sb"
          onTextClick={() => setShowSaveModal(true)}
        >
          <LeftIcon className="w-5 h-10 text-primary" />
        </TopBar>
      </div>

      <div className="flex flex-col gap-6 px-6 pt-6">
        {/* 이미지 */}
        <label className="relative w-full h-[200px] cursor-pointer">
          {src ? (
            <img
              src={src}
              alt="여행 이미지"
              className="w-full h-full object-cover rounded-10"
            />
          ) : (
            <div className="w-full h-full bg-neutral rounded-10" />
          )}
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-10">
            <CameraIcon className="w-8 h-8 text-white" />
          </div>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden"
          />
        </label>

        {/* 여행 제목 */}
        <div className="flex flex-col gap-2">
          <p className="text-14-sb text-black1">여행 제목</p>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={trip.title}
            className="w-full bg-neutral rounded-10 px-4 py-3 text-14-rg text-black1 outline-none"
          />
        </div>
      </div>
    </div>
  );
}
