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
    { label: '전시/예술', value: 'exhibition/art' },
    { label: '공연/문화', value: 'performance/culture' },
    { label: '액티비티', value: 'activity' },
    { label: '실내오락', value: 'indoor' },
    { label: '쇼핑', value: 'shopping' },
    { label: '공방/소품', value: 'workshop' },
    { label: '자연/관광', value: 'nature' },
    { label: '술/바', value: 'bar' },
  ];

  return (
    <SelectionLayout
      step={8}
      url="/select/mood"
      icon="🏄️"
      text1="어떤 활동을"
      text2="원하세요?"
      onNext={() => navigate('/select/dislike')}
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
