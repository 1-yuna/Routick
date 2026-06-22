import { useState } from 'react';
import BaseModal from '../../../common/modal/BaseModal.jsx';

// 저장 - 여행 제목 입력 모달창
export default function TitleInputModal({ onConfirm, onCancel }) {
  const [title, setTitle] = useState('');

  return (
    <BaseModal onConfirm={() => onConfirm(title)} onCancel={onCancel}>
      <p className="text-16-sb text-black1">저장할 여행 제목을 입력해주세요!</p>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full h-10 border border-line2 rounded-[5px] px-3 text-14-rg text-black1 outline-none mt-2"
      />
    </BaseModal>
  );
}
