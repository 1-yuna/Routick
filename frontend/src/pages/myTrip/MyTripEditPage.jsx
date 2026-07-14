import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import CameraIcon from '../../assets/icons/camera.svg?react';
import BaseModal from '../../common/modal/BaseModal.jsx';
import useMyTripStore from '../../store/myTripStore.jsx';
import { getImageUrl } from '../../utils/imageUtil.jsx';
import { updateTrip } from '../../api/trip.jsx';

export default function MyTripEditPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const trip = location.state;

  const updateTripTitle = useMyTripStore((state) => state.updateTripTitle);
  const updateTripImage = useMyTripStore((state) => state.updateTripImage);

  const [title, setTitle] = useState(trip?.title ?? '');
  const [src, setSrc] = useState(getImageUrl(trip?.coverImageUrl));
  const [coverImageFile, setCoverImageFile] = useState(null);
  const [showSaveModal, setShowSaveModal] = useState(false);

  if (!trip) return null;

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setCoverImageFile(file);
    setSrc(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    try {
      const finalTitle = title.trim() || trip.title;
      const res = await updateTrip(trip.tripId, finalTitle, coverImageFile);
      const updated = res.data.data; // { tripId, title, coverImageUrl }
      updateTripTitle(updated.tripId, updated.title);
      if (updated.coverImageUrl)
        updateTripImage(updated.tripId, updated.coverImageUrl);
      setShowSaveModal(false);
      navigate('/mytrip', { state: { isEditing: true } });
    } catch (e) {
      setShowSaveModal(false);
      alert('저장에 실패했어요. 다시 시도해주세요.');
    }
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
          onClick={() => navigate('/mytrip', { state: { isEditing: true } })}
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
