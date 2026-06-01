import CheckIcon from '../../../assets/icons/check.svg?react';

// 저장 - 확인용 모달
export default function SaveCompleteModal({ onConfirm }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-[10px] p-5 w-[298px] flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
          <CheckIcon className="w-6 h-6 text-white" />
        </div>
        <div className="flex flex-col items-center gap-1">
          <p className="text-16-sb text-black1">저장이 완료되었어요!</p>
          <p className="text-12-rg text-gray2">내 여행에서 확인해보세요</p>
        </div>
        <button
          onClick={onConfirm}
          className="w-full h-10 border border-line2 rounded-[5px] text-14-sb text-gray2"
        >
          확인
        </button>
      </div>
    </div>
  );
}
