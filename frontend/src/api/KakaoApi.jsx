import axios from 'axios';

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_REST_API_KEY;

// 장소 찾기 Kakao API
export const searchPlaces = async (query) => {
  const res = await axios.get(
    `https://dapi.kakao.com/v2/local/search/keyword.json`,
    {
      params: { query },
      headers: { Authorization: `KakaoAK ${KAKAO_API_KEY}` },
    }
  );
  return res.data.documents;
};
