import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 4단계 - 연령대 (단일 선택)
export default function AgeGroupPage() {
  const navigate = useNavigate();
  const age = useSelectionStore((state) => state.age);
  const setAge = useSelectionStore((state) => state.setAge);

  const AGE_OPTIONS = [
    { label: '10대', value: 'teens' },
    { label: '20대', value: 'twenties' },
    { label: '30대', value: 'thirties' },
    { label: '40대', value: 'forties' },
    { label: '50대 이상', value: 'fifties_over' },
  ];

  return (
    <SelectionLayout
      step={4}
      icon="🪪"
      text1="여행자 연령대가"
      text2="어떻게 되세요?"
      onNext={() => navigate('/select/mood')}
      disabled={!age}
    >
      <SelectionGrid items={AGE_OPTIONS} selected={age} onSelect={setAge} />
    </SelectionLayout>
  );
}
