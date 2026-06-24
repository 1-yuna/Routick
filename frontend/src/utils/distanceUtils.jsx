// Haversine 공식으로 두 좌표 간 거리 계산 (단위: km)
export function calcDistanceKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// 이동수단별 거리 제한 초과 여부 반환
// transport: 'walk' | 'car'
// 도보 3km, 자동차 20km 초과 시 에러 메시지 반환, 정상이면 null
export function getDistanceError(lat1, lng1, lat2, lng2, transport) {
  if (!lat1 || !lng1 || !lat2 || !lng2) return null;

  const distKm = calcDistanceKm(lat1, lng1, lat2, lng2);
  const limit = transport === 'walk' ? 3 : 20;

  if (distKm > limit) {
    return '두 지점이 너무 멀어요. 가까운 지역으로 다시 입력해주세요';
  }
  return null;
}
