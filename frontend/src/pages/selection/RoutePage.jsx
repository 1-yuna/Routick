import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

const ROUTE_OPTIONS = [
  { label: '목적지', value: 'destination' },
  { label: '출발·도착지', value: 'route' },
];

// 선택 4단계 - 여행 동선 여부 (CS-05)
export default function RoutePage() {
  const route = useSelectionStore((state) => state.route);
  const setRoute = useSelectionStore((state) => state.setRoute);
  const navigate = useNavigate();

  return (
    <SelectionLayout
      step={4}
      url="/select/transport"
      icon="✈️"
      text1="여행 동선이"
      text2="정해져 있나요?"
      onNext={() => navigate('/select/address')}
      disabled={!route}
    >
      <SelectionGrid
        items={ROUTE_OPTIONS}
        selected={route}
        onSelect={setRoute}
      />
    </SelectionLayout>
  );
}
