import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 5단계 - 분위기 선호 선택 (다중 선택)
export default function MoodPage() {
  const mood = useSelectionStore((state) => state.mood);
  const setMood = useSelectionStore((state) => state.setMood);
  const navigate = useNavigate();

  const MOOD_OPTIONS = [
    { label: '활기찬', value: 'energetic' },
    { label: '힐링', value: 'healing' },
    { label: '감성', value: 'emotional' },
    { label: '조용한', value: 'quiet' },
    { label: '따뜻한', value: 'warm' },
    { label: '로맨틱', value: 'romantic' },
    { label: '깔끔한', value: 'clean' },
    { label: '빈티지', value: 'vintage' },
    { label: '힙한', value: 'hip' },
  ];

  return (
    <SelectionLayout
      step={7}
      icon="🌅"
      text1="어떤 분위기를"
      text2="원하세요?"
      onNext={() => navigate('/select/activity')}
      disabled={mood.length === 0}
      subText="다중선택이 가능해요"
    >
      <div className="overflow-y-auto no-scrollbar max-h-80">
        <SelectionGrid
          items={MOOD_OPTIONS}
          selected={mood}
          onSelect={setMood}
        />
      </div>
    </SelectionLayout>
  );
}
