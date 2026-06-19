import { useNavigate } from 'react-router-dom';

import SelectionLayout from '../../components/selection/SelectionLayout.jsx';
import SelectionInput from '../../common/input/SelectionInput.jsx';
import FieldMessage from '../../common/text/FieldMessage.jsx';
import useSelectionStore from '../../store/selectionStore.jsx';

const PERIOD_DAYS = { day: 1, '1n2d': 2, '2n3d': 3, '3n4d': 4 };
const EMPTY_PLACE = { name: '', lat: '', lng: '', placeId: '' };

// 선택 5단계 - 여행 장소 입력 (CS-06)
export default function AddressPage() {
  const navigate = useNavigate();
  const route = useSelectionStore((state) => state.route);
  const period = useSelectionStore((state) => state.period);
  const address = useSelectionStore((state) => state.address);
  const addresses = useSelectionStore((state) => state.addresses);

  const totalDays = PERIOD_DAYS[period] ?? 1;
  const dayList = Array.from({ length: totalDays }, (_, i) => ({
    start: addresses[i]?.start ?? EMPTY_PLACE,
    end: addresses[i]?.end ?? EMPTY_PLACE,
  }));

  const navigateToSearch = (dayIdx, field) => {
    navigate('/select/address/search', {
      state: { dayIdx, field, returnTo: 'route' },
    });
  };

  const isDestinationReady = address.name !== '';
  const isRouteReady = dayList.every(
    (day) => day.start.name !== '' && day.end.name !== ''
  );
  const isReady = route === 'destination' ? isDestinationReady : isRouteReady;
  const distanceError = null;

  if (route === 'destination') {
    return (
      <SelectionLayout
        step={5}
        icon="🔍"
        text1="가고자 하는 여행"
        text2="장소를 입력해주세요"
        onNext={() => navigate('/select/companion')}
        disabled={!isReady}
      >
        <SelectionInput
          placeholder="장소, 주소 검색"
          value={address.name}
          onClick={() =>
            navigate('/select/address/search', {
              state: { returnTo: 'destination' },
            })
          }
        />
      </SelectionLayout>
    );
  }

  return (
    <SelectionLayout
      step={5}
      icon="🔍"
      text1="가고자 하는 여행"
      text2="장소를 입력해주세요"
      subText="1박 이상인 경우, 도착지를 목소로 입력해주세요"
      onNext={() => navigate('/select/companion')}
      disabled={!isReady}
      contentGap="gap-[28px]"
    >
      <div className="flex flex-col gap-4 overflow-y-auto no-scrollbar">
        {dayList.map((day, i) => (
          <div key={i} className="flex flex-col gap-2">
            <p className="text-16-sb text-gray2">Day {i + 1}</p>
            <div className="flex flex-col gap-1">
              <SelectionInput
                placeholder="출발지"
                value={day.start.name}
                onClick={() => navigateToSearch(i, 'start')}
              />
              {distanceError && i === 0 && (
                <FieldMessage type="error">{distanceError}</FieldMessage>
              )}
              <SelectionInput
                placeholder="도착지"
                value={day.end.name}
                onClick={() => navigateToSearch(i, 'end')}
              />
            </div>
          </div>
        ))}
      </div>
    </SelectionLayout>
  );
}
