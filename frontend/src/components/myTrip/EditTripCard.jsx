import CameraIcon from '../../assets/icons/camera.svg?react';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import ImageIcon from '../../assets/icons/image.svg?react';
import CheckIcon from '../../assets/icons/check.svg?react';
import { useState } from 'react';
import useMyTripStore from '../../store/myTripStore.jsx';
import BaseModal from '../../common/modal/BaseModal.jsx';

// 여행 편집 카드
export default function EditTripCard({ trip, isChecked, onCheck }) {
  const { title, src } = trip;
  const [showImageSheet, setShowImageSheet] = useState(false);
  const [isImageSelected, setIsImageSelected] = useState(false);
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [newTitle, setNewTitle] = useState(title);

  const updateTripImage = useMyTripStore((state) => state.updateTripImage);
  const updateTripTitle = useMyTripStore((state) => state.updateTripTitle);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const imageUrl = URL.createObjectURL(file);
    updateTripImage(trip.id, imageUrl);
    setShowImageSheet(false);
  };

  const handleTitleConfirm = () => {
    updateTripTitle(trip.id, newTitle);
    setShowTitleModal(false);
  };

  return (
    <div
      className={`flex items-center p-2 gap-2 ${isChecked || isImageSelected ? 'bg-button' : 'bg-default'}`}
    >
      {/*체크박스*/}
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-primary border-primary' : 'border-line2'}`}
      >
        {isChecked && <CheckIcon className="text-white w-4 h-4">✓</CheckIcon>}
      </button>

      {/*카드*/}
      <div className="flex h-[82px] flex-1 bg-white rounded-10 shadow-md">
        <div className="relative flex-shrink-0">
          <img
            src={src}
            alt={title}
            className="w-24 h-full rounded-l-10 object-cover"
          />
          <div className="absolute inset-0 bg-black/45 rounded-l-10" />
        </div>
        {/*제목*/}
        <p
          className="px-3 py-2 text-14-sb text-black1 cursor-pointer flex-1"
          onClick={() => setShowTitleModal(true)}
        >
          {title}
        </p>
      </div>

      {/* 제목 수정 모달 */}
      {showTitleModal && (
        <BaseModal
          onConfirm={handleTitleConfirm}
          onCancel={() => setShowTitleModal(false)}
        >
          <p className="text-14-sb text-black1 text-center mb-3">
            제목을 수정해주세요
          </p>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="w-full h-9 bg-neutral rounded-5 px-3 py-2 text-12-rg text-gray2 outline-none"
          />
        </BaseModal>
      )}
    </div>
  );
}
