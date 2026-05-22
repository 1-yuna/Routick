import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import SelectionInput from '../../common/input/SelectionInput.jsx';
import SelectionLayout from '../../components/selection/SelectionLayout.jsx';

// 선택1 - 주소 찾기
export default function AddressPage() {
  const navigate = useNavigate();
  const [address, setAddress] = useState('');

  return (
    <SelectionLayout
      step={1}
      icon="✈️"
      text1="가고자 하는 여행"
      text2="주소를 검색해주세요"
      onNext={() => console.log('next')}
    >
      <SelectionInput
        placeholder="장소, 주소 검색"
        value={address}
        onClick={() => navigate('/course/address/search')}
      />
    </SelectionLayout>
  );
}
