import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import SelectionInput from '../../common/input/SelectionInput.jsx';
import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import CancelIcon from '../../assets/icons/cancel.svg?react';
import useSelectionStore from '../../store/selectionStore.jsx';

function KeywordTag({ keyword, onRemove }) {
  return (
    <div className="flex items-center gap-1 px-3 py-1 rounded-full border border-line2 text-14-rg text-gray2">
      {keyword}
      <CancelIcon
        className="w-3 h-3 text-gray2 cursor-pointer"
        onClick={onRemove}
      />
    </div>
  );
}

// 선택 8단계 - 비선호 키워드 (다중 입력)
export default function DislikeActivityPage() {
  const dislike = useSelectionStore((state) => state.dislike);
  const addDislike = useSelectionStore((state) => state.addDislike);
  const removeDislike = useSelectionStore((state) => state.removeDislike);
  const navigate = useNavigate();
  const [input, setInput] = useState('');

  const handleKeyDown = (e) => {
    if (e.nativeEvent.isComposing) return;

    if (e.key === 'Enter') {
      e.preventDefault();

      const keyword = input.trim();

      if (!keyword) return;

      addDislike(keyword);
      setInput('');
    }
  };

  return (
    <SelectionLayout
      step={9}
      url="/select/activity"
      icon="🤔"
      text1="피하고 싶은"
      text2="활동이 있으신가요?"
      buttonText={dislike.length > 0 ? '다음' : '건너뛰기'}
      onNext={() => navigate('/loading')}
    >
      <div className="flex flex-col gap-3">
        <SelectionInput
          placeholder="키워드로 작성해주세요.  ex.노래방"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="flex flex-wrap gap-2">
          {dislike.map((keyword) => (
            <KeywordTag
              key={keyword}
              keyword={keyword}
              onRemove={() => removeDislike(keyword)}
            />
          ))}
        </div>
      </div>
    </SelectionLayout>
  );
}
