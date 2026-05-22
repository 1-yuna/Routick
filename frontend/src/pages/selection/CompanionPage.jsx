import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionGrid from '../../components/selection/SelectionGrid.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';
import { useNavigate } from 'react-router-dom';

// 선택2 - 여행 기간
export default function CompanionPage() {
  const navigate = useNavigate();
  const companion = useSelectionStore((state) => state.companion);
  const setCompanion = useSelectionStore((state) => state.setCompanion);

  const COMPANION_OPTIONS = [
    { label: '홀로', value: 'solo' },
    { label: '연인', value: 'couple' },
    { label: '친구', value: 'friend' },
    { label: '부모님과', value: 'parents' },
    { label: '자녀와', value: 'children' },
    { label: '반려동물과', value: 'pet' },
  ];

  return (
    <SelectionLayout
      step={3}
      icon="👫"
      text1="누구와 함께"
      text2="가시나요?"
      onNext={() => navigate('/select/age')}
      disabled={!companion}
    >
      <SelectionGrid
        items={COMPANION_OPTIONS}
        selected={companion}
        onSelect={setCompanion}
      />
    </SelectionLayout>
  );
}
