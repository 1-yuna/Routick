import { useState } from 'react';
import LeftIcon from '../../assets/icons/left.svg?react';
import CloseIcon from '../../assets/icons/close.svg?react';
import MapIcon from '../../assets/icons/map.svg?react';
import { useLocation, useNavigate } from 'react-router-dom';
import SelectionInput from '../../common/input/SelectionInput.jsx';

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_REST_API_KEY;

// 선택1 - 주소 찾기(2)
export default function AddressSearchPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [query, setQuery] = useState(location.state?.address || '');
  const [results, setResults] = useState([]);

  const handleChange = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.length < 2) {
      setResults([]);
      return;
    }

    const res = await fetch(
      `https://dapi.kakao.com/v2/local/search/keyword.json?query=${value}`,
      { headers: { Authorization: `KakaoAK ${KAKAO_API_KEY}` } }
    );
    const data = await res.json();
    setResults(data.documents);
  };

  const handlePlaceSelect = (place) => {
    console.log(place.place_name, place.x, place.y);
    setResults([]);
    setQuery(place.place_name);
    console.log('이동:', place.place_name);
    navigate('/course/address', { state: { address: place.place_name } });
  };

  return (
    <div className="pt-12 px-6 gap-5 h-screen pb-28 flex flex-col bg-default">
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
      <div>
        {results.map((place) => (
          <div
            className="flex p-3 gap-5 border-b border-line1"
            key={place.id}
            onClick={() => handlePlaceSelect(place)}
          >
            {/*아이콘*/}
            <div className="flex items-center justify-center w-[35px] h-[35px] rounded-full bg-button">
              <MapIcon className="w-5 h-5 text-gray2" />
            </div>

            {/*장소*/}
            <div className="flex flex-col">
              <div className="text-14-sb text-black1">{place.place_name}</div>
              <div className="text-12-rg text-gray2">{place.address_name}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
