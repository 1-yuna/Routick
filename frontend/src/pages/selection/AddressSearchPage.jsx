import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { searchPlaces } from '../../api/KakaoApi.jsx';
import SelectionInput from '../../common/input/SelectionInput.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import CloseIcon from '../../assets/icons/close.svg?react';
import MapIcon from '../../assets/icons/map.svg?react';
import useSelectionStore from '../../store/selectionStore.jsx';

// 장소 검색
export default function AddressSearchPage() {
  const setAddress = useSelectionStore((state) => state.setAddress);
  const setAddresses = useSelectionStore((state) => state.setAddresses);
  const addresses = useSelectionStore((state) => state.addresses);
  const location = useLocation();
  const navigate = useNavigate();
  const mode = location.state?.mode;
  const dayNumber = location.state?.dayNumber ?? 1; // ResultPage에서 넘겨준 selectedDay
  const [query, setQuery] = useState(location.state?.address?.name || '');
  const [results, setResults] = useState([]);

  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);
    setResults(value.length >= 2 ? await searchPlaces(value) : []);
  };

  const handlePlaceSelect = ({ place_name, x, y, id }) => {
    const selectedPlace = {
      name: place_name,
      lat: Number(y),
      lng: Number(x),
      placeId: id,
    };

    if (mode === 'add') {
      // dayNumber를 PlaceDetailPage로 전달
      navigate(`/place/${id}`, {
        state: {
          ...selectedPlace,
          mode: 'add',
          dayNumber,
        },
      });
      return;
    }

    const { dayIdx, field, returnTo } = location.state || {};

    if (returnTo === 'destination') {
      setAddress(selectedPlace);
    }

    if (returnTo === 'route') {
      const updated = [...addresses];
      updated[dayIdx] = {
        ...updated[dayIdx],
        [field]: selectedPlace,
      };
      setAddresses(updated);
    }

    navigate('/select/address');
  };

  return (
    <div className="pt-12 px-6 gap-5 h-screen pb-28 flex flex-col bg-default">
      <SelectionInput
        value={query}
        onChange={handleChange}
        placeholder="주소, 장소 검색"
        leftIcon={
          <LeftIcon
            className="w-5 h-10 text-line2"
            onClick={() => navigate(-1)}
          />
        }
        rightIcon={
          <CloseIcon
            className="w-6 h-6 text-gray1"
            onClick={(e) => {
              e.stopPropagation();
              setQuery('');
            }}
          />
        }
      />
      <div>
        {results.map((place) => (
          <PlaceItem key={place.id} place={place} onClick={handlePlaceSelect} />
        ))}
      </div>
    </div>
  );
}

function PlaceItem({ place, onClick }) {
  return (
    <div
      className="flex p-3 gap-5 border-b border-line1"
      onClick={() => onClick(place)}
    >
      <div className="flex items-center justify-center w-[35px] h-[35px] rounded-full bg-button">
        <MapIcon className="w-5 h-5 text-gray2" />
      </div>
      <div className="flex flex-col">
        <div className="text-14-sb text-black1">{place.place_name}</div>
        <div className="text-12-rg text-gray2">{place.address_name}</div>
      </div>
    </div>
  );
}
