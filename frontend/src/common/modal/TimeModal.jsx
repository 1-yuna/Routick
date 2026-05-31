// common/modal/TimeModal.jsx
export default function TimeModal({ text, children, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-[10px] p-5 w-[298px] h-[144px] flex flex-col justify-between">
        <p className="text-16-sb text-gray2">{text}</p>
        {children}
        <div className="flex justify-between">
          <button
            onClick={onCancel}
            className="w-[120px] h-7 rounded-[5px] border border-line2 text-14-sb text-gray2"
          >
            취소
          </button>
          <button
            onClick={onConfirm}
            className="w-[120px] h-7 rounded-[5px] border border-line2 text-14-sb text-gray2"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}
