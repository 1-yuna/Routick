import { getPlaceList } from '../api/place.jsx';

const cache = new Map(); // key: `${category}_${regionName}` -> Promise<items[]>

const buildKey = (category, regionName) => `${category}_${regionName}`;

// 홈에서 미리 호출 - 캐시에 없을 때만 요청 시작 (결과 기다리지 않음)
export const prefetchPlaceList = (category, regionName, lat, lng) => {
  const key = buildKey(category, regionName);
  if (cache.has(key)) return;
  const promise = getPlaceList(category, regionName, lat, lng)
    .then((res) => res.data.data.items)
    .catch((e) => {
      cache.delete(key); // 실패하면 캐시에서 지워서 재시도 가능하게
      throw e;
    });
  cache.set(key, promise);
};

// PlayListPage에서 사용 - 캐시에 이미 있으면 그 프로미스를, 없으면 새로 요청해서 반환
export const getCachedPlaceList = (category, regionName, lat, lng) => {
  const key = buildKey(category, regionName);
  if (!cache.has(key)) {
    prefetchPlaceList(category, regionName, lat, lng);
  }
  return cache.get(key);
};
