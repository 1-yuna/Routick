import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 6단계 - 활동 선택 (다중 선택)
export default function ActivityPage() {
  const activity = useSelectionStore((state) => state.activity);
  const setActivity = useSelectionStore((state) => state.setActivity);
  const navigate = useNavigate();

  const ACTIVITY_OPTIONS = [
    { label: '관광/전시', value: 'sightseeing' },
    { label: '공연/문화', value: 'performance' },
    { label: '스릴/체험', value: 'thrill' },
    { label: '오락/스포츠', value: 'sports' },
    { label: '자연/선택', value: 'nature' },
    { label: '쇼핑', value: 'shopping' },
    { label: '실내오락', value: 'indoor' },
    { label: '술/바', value: 'bar' },
  ];

  return (
    <SelectionLayout
      step={6}
      icon="🏄️"
      text1="어떤 활동을"
      text2="원하세요?"
      onNext={() => navigate('/select/transport')}
      disabled={activity.length === 0}
      subText="다중선택이 가능해요"
    >
      <div className="overflow-y-auto no-scrollbar max-h-80">
        <SelectionGrid
          items={ACTIVITY_OPTIONS}
          selected={activity}
          onSelect={setActivity}
        />
      </div>
    </SelectionLayout>
  );
}
