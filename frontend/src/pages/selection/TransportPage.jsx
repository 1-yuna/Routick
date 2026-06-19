import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 6단계 - 이동 수단 (단일 선택)
export default function TransportPage() {
  const transport = useSelectionStore((state) => state.transport);
  const setTransport = useSelectionStore((state) => state.setTransport);
  const navigate = useNavigate();

  const TRANSPORT_OPTIONS = [
    { label: '도보', value: 'walk' },
    { label: '자동차', value: 'car' },
  ];

  return (
    <SelectionLayout
      step={3}
      icon="🚘"
      text1="이동 수단이"
      text2="어떻게 되세요?"
      onNext={() => navigate('/select/route')}
      disabled={!transport}
    >
      <SelectionGrid
        items={TRANSPORT_OPTIONS}
        selected={transport}
        onSelect={setTransport}
      />
    </SelectionLayout>
  );
}
