import { useState } from 'react';
import BaseModal from '../../../common/modal/BaseModal.jsx';

// 저장 - 여행 제목 입력 모달창
export default function TitleInputModal({ onConfirm, onCancel }) {
  const [title, setTitle] = useState('');

  return (
    <BaseModal onConfirm={() => onConfirm(title)} onCancel={onCancel}>
      <p className="text-14-sb text-black1 text-center leading-relaxed mb-3">
        저장할 여행 제목을
        <br />
        입력해주세요!
      </p>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="제목을 입력하세요."
        className="w-full h-9 bg-neutral rounded-5 px-3 py-2 text-12-rg text-gray2 outline-none placeholder:text-gray2"
      />
    </BaseModal>
  );
}
