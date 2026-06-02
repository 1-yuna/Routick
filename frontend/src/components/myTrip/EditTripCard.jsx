import CameraIcon from '../../assets/icons/camera.svg?react';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import ImageIcon from '../../assets/icons/image.svg?react';
import { useState } from 'react';
import useMyTripStore from '../../store/myTripStore.jsx';

// 여행 편집 카드
export default function EditTripCard({ trip, isChecked, onCheck }) {
  const { title, src } = trip;
  const [showImageSheet, setShowImageSheet] = useState(false);
  const [isImageSelected, setIsImageSelected] = useState(false);

  const updateTripImage = useMyTripStore((state) => state.updateTripImage);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const imageUrl = URL.createObjectURL(file);
    // store에 저장
    updateTripImage(trip.id, imageUrl);
    setShowImageSheet(false);
  };

  return (
    <div
      className={`flex items-center p-2 gap-3 ${isChecked || isImageSelected ? 'bg-line1' : 'bg-login'}`}
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
          <div
            className="absolute inset-0 flex flex-col items-center justify-center gap-1 cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              setIsImageSelected(true);
              setShowImageSheet(true);
            }}
          >
            <CameraIcon className="w-6 h-6 text-white" />
            <span className="text-10-rg text-white">커버</span>
          </div>

          {/*이미지 선택 시트*/}
          {showImageSheet && (
            <div
              className="fixed inset-0 z-50 bg-black/40"
              onClick={() => {
                setShowImageSheet(false);
                setIsImageSelected(false);
              }}
            >
              <div
                className="absolute bottom-0 left-0 w-full h-40 bg-white rounded-t-[5px] p-5"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-center items-center mb-4">
                  <p className="text-16-sb text-black1">사진 첨부</p>
                  <button
                    className="absolute right-5"
                    onClick={() => {
                      setShowImageSheet(false);
                      setIsImageSelected(false);
                    }}
                  >
                    <CancelIcon className="w-5 h-5 text-gray2" />
                  </button>
                </div>
                <button
                  className="flex items-center gap-3 w-full py-3 text-black1"
                  onClick={() =>
                    document.getElementById(`file-${trip.id}`).click()
                  }
                >
                  <ImageIcon className="w-5 h-5" />
                  <span className="text-14-rg">사진첩</span>
                </button>
                <input
                  id={`file-${trip.id}`}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageChange}
                />
              </div>
            </div>
          )}
        </div>
        <p className="p-3 text-14-sb text-black1">{title}</p>
      </div>
    </div>
  );
}
