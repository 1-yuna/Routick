import CameraIcon from '../../assets/icons/camera.svg?react';

// 이미지가 없을 경우 - 기본 이미지
export default function PlaceImageDefault({ className }) {
  return (
    <div className={`bg-button flex items-center justify-center ${className}`}>
      <CameraIcon className="w-8 h-8 text-gray1" />
    </div>
  );
}
