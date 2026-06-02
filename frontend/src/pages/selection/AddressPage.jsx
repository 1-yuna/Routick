import { useNavigate } from 'react-router-dom';

import SelectionInput from '../../common/input/SelectionInput.jsx';
import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 1단계 - 주소 페이지
export default function AddressPage() {
  const address = useSelectionStore((state) => state.address);
  const navigate = useNavigate();

  return (
    <SelectionLayout
      step={1}
      url="/home"
      icon="✈️"
      text1="가고자 하는 여행"
      text2="주소를 검색해주세요"
      onNext={() => navigate('/select/period')}
      disabled={!address.name}
    >
      <SelectionInput
        placeholder="장소, 주소 검색"
        value={address.name}
        onClick={() =>
          navigate('/select/address/search', { state: { address } })
        }
      />
    </SelectionLayout>
  );
}
