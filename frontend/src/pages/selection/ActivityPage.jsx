import SelectionLayout from '../../components/selection/SelectionLayout.jsx';

// 선택1 - 주소 찾기
export default function ActivityPage() {
  return (
    <SelectionLayout
      step={1}
      url="/home"
      icon="✈️"
      text1="가고자 하는 여행"
      text2="주소를 검색해주세요"
      onNext={() => console.log('next')}
    ></SelectionLayout>
  );
}
