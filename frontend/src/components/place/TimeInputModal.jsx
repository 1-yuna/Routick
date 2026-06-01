import { useState } from 'react';
import TimeModal from '../../common/modal/TimeModal.jsx';

// 머무를 시간 입력 모달 - 시간(0~23):분(0~59) 입력 후 분 단위로 변환해서 전달
export default function TimeInputModal({ onConfirm, onCancel }) {
  const [hour, setHour] = useState('01');
  const [minute, setMinute] = useState('00');

  return (
    <TimeModal
      text="머무를 시간을 입력해주세요!"
      onConfirm={() => onConfirm(Number(hour) * 60 + Number(minute))}
      onCancel={onCancel}
    >
      {/*시간:분 입력*/}
      <div className="flex gap-1">
        <input
          type="number"
          value={hour}
          min="0"
          max="23"
          onChange={(e) => {
            const val = Math.min(23, Math.max(0, Number(e.target.value)));
            setHour(String(val).padStart(2, '0'));
          }}
          className="w-8 h-8 border border-line2 text-center text-16-sb text-gray2 outline-none"
        />
        <span className="text-16-sb text-black1">:</span>
        <input
          type="number"
          value={minute}
          min="0"
          max="59"
          onChange={(e) => {
            const val = Math.min(59, Math.max(0, Number(e.target.value)));
            setMinute(String(val).padStart(2, '0'));
          }}
          className="w-8 h-8 border border-line2 text-center text-16-sb text-gray2 outline-none"
        />
      </div>
    </TimeModal>
  );
}
