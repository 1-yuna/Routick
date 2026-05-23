import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SelectionInput from '../../common/input/SelectionInput.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';
import CloseIcon from '../../assets/icons/close.svg?react';
import MapIcon from '../../assets/icons/map.svg?react';
import useSelectionStore from '../../store/selectionStore.jsx';

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_REST_API_KEY;

// API 호출
const searchPlaces = async (query) => {
  const res = await fetch(
    `https://dapi.kakao.com/v2/local/search/keyword.json?query=${query}`,
    { headers: { Authorization: `KakaoAK ${KAKAO_API_KEY}` } }
  );
  const data = await res.json();
  return data.documents;
};

// 장소 검색
export default function AddressSearchPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState(location.state?.address || '');
  const [results, setResults] = useState([]);
  const setAddress = useSelectionStore((state) => state.setAddress);

  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);
    setResults(value.length >= 2 ? await searchPlaces(value) : []);
  };

  const handlePlaceSelect = ({ place_name, x, y, id }) => {
    setAddress({ name: place_name, x, y, placeId: id });
    navigate('/select/address');
  };

  return (
    <div className="pt-12 px-6 gap-5 h-screen pb-28 flex flex-col bg-default">
      {/*장소 검색*/}
      <SelectionInput
        value={query}
        onChange={handleChange}
        placeholder="주소, 장소 검색"
        leftIcon={
          <LeftIcon
            className="w-5 h-5 text-gray2"
            onClick={() => navigate(-1)}
          />
        }
        rightIcon={
          <CloseIcon
            className="w-5 h-5 text-gray2"
            onClick={(e) => {
              e.stopPropagation();
              setQuery('');
            }}
          />
        }
      />
      {/*장소 반환*/}
      <div>
        {results.map((place) => (
          <PlaceItem key={place.id} place={place} onClick={handlePlaceSelect} />
        ))}
      </div>
    </div>
  );
}

// 장소 리스트
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
