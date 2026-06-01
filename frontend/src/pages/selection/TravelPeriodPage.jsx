import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 2선택 - 여행 기간 (단일 선택)
export default function TravelPeriodPage() {
  const navigate = useNavigate();
  const period = useSelectionStore((state) => state.period);
  const setPeriod = useSelectionStore((state) => state.setPeriod);

  const PERIOD_OPTIONS = [
    { label: '당일치기', value: 'day' },
    { label: '1박 2일', value: '1n2d' },
    { label: '2박 3일', value: '2n3d' },
    { label: '3박 4일', value: '3n4d' },
  ];

  return (
    <SelectionLayout
      step={2}
      url="/select/address"
      icon="🗓"
      text1="여행 기간이"
      text2="어떻게 되세요?"
      onNext={() => navigate('/select/companion')}
      disabled={!period}
    >
      <SelectionGrid
        items={PERIOD_OPTIONS}
        selected={period}
        onSelect={setPeriod}
      />
    </SelectionLayout>
  );
}
