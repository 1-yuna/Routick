import CheckIcon from '../../../assets/icons/check.svg?react';
import BaseModal from '../../../common/modal/BaseModal.jsx';

// 저장 - 확인용 모달
export default function SaveCompleteModal({ onConfirm }) {
  return (
    <BaseModal confirmOnly onConfirm={onConfirm}>
      <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center mb-3">
        <CheckIcon className="w-6 h-6 text-white" />
      </div>
      <p className="text-14-sb text-black1">저장이 완료되었어요!</p>
      <p className="text-12-rg text-gray2">내 여행에서 확인해보세요</p>
    </BaseModal>
  );
}
