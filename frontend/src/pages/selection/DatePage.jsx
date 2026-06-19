import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import DateCalendar from '../../components/selection/DateCalendar.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

// 선택 2단계 - 여행 날짜 선택 (CS-03)
export default function DatePage() {
  const period = useSelectionStore((state) => state.period);
  const setDate = useSelectionStore((state) => state.setDate);
  const navigate = useNavigate();

  const [dateRange, setDateRange] = useState({ start: null, end: null });

  const handleNext = () => {
    setDate(dateRange);
    navigate('/select/transport');
  };

  return (
    <SelectionLayout
      step={2}
      icon="🗓️"
      text1="여행 날짜를"
      text2="선택해주세요"
      onNext={handleNext}
      disabled={!dateRange.start}
      contentGap="gap-8"
    >
      <DateCalendar value={dateRange} onChange={setDateRange} period={period} />
    </SelectionLayout>
  );
}
