import { useState } from 'react';
import BaseModal from '../../common/modal/BaseModal.jsx';

// 장소 추가 모달 - 머무를 시간 + 장소 종류 입력
export default function PlaceInfoModal({ onConfirm, onCancel }) {
  const [hour, setHour] = useState('01');
  const [minute, setMinute] = useState('00');
  const [category, setCategory] = useState('etc');

  return (
    <BaseModal
      text="장소 정보를 입력해주세요!"
      onConfirm={() =>
        onConfirm({ stayTime: Number(hour) * 60 + Number(minute), category })
      }
      onCancel={onCancel}
    >
      {/*머무를 시간*/}
      <div className="flex flex-col gap-2">
        <p className="text-12-rg text-gray2">머무를 시간</p>
        <div className="flex gap-1 items-center">
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
      </div>

      {/*장소 종류*/}
      <div className="flex flex-col gap-2">
        <p className="text-12-rg text-gray2">장소 종류</p>
        <div className="flex gap-2">
          {[
            { label: '🍽️ 음식', value: 'food' },
            { label: '🏨 숙소', value: 'lodging' },
            { label: '기타', value: 'etc' },
          ].map((item) => (
            <button
              key={item.value}
              onClick={() => setCategory(item.value)}
              className={`flex-1 h-8 rounded-[5px] text-12-sb border transition-colors
                ${
                  category === item.value
                    ? item.value === 'food'
                      ? 'bg-[#FAEEDA] border-food text-[#633806]'
                      : item.value === 'lodging'
                        ? 'bg-[#E1F5EE] border-lodging text-[#085041]'
                        : 'bg-primaryOpacity border-primary text-primary'
                    : 'bg-button border-line2 text-gray2'
                }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </BaseModal>
  );
}
