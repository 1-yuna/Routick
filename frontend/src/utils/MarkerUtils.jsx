// 마커 색상 상수
const MARKER_COLOR = {
  place: '#4B5FDC',
  parking: '#FFB705',
  mark: '#FF8A5C', // 출발지(S) / 도착지(E)
};
// - place: 모두 primary(#4B5FDC), 번호는 blocks 내 위치 기준으로 매번 새로 계산
// - parking: 주황(#FFB705), 연속 그룹의 마지막만 표시
// - start(S) / end(E): mark(#FF8A5C)
export function extractMarkers(blocks, dayData = null) {
  const markers = [];

  // 출발지 S 마커
  if (dayData?.start?.lat && dayData?.start?.lng) {
    markers.push({
      lat: dayData.start.lat,
      lng: dayData.start.lng,
      color: MARKER_COLOR.mark,
      label: 'S',
      type: 'start',
    });
  }

  let placeCount = 0;
  let i = 0;
  while (i < blocks.length) {
    const block = blocks[i];

    if (block.type === 'place') {
      placeCount++;
      markers.push({
        lat: block.lat,
        lng: block.lng,
        color: MARKER_COLOR.place,
        label: String(placeCount),
        type: 'place',
      });
    } else if (block.type === 'parking') {
      let last = block;
      while (i + 1 < blocks.length && blocks[i + 1].type === 'parking') {
        i++;
        last = blocks[i];
      }
      markers.push({
        lat: last.lat,
        lng: last.lng,
        color: MARKER_COLOR.parking,
        label: 'P',
        type: 'parking',
      });
    }

    i++;
  }

  // 도착지 E 마커
  if (dayData?.end?.lat && dayData?.end?.lng) {
    markers.push({
      lat: dayData.end.lat,
      lng: dayData.end.lng,
      color: MARKER_COLOR.mark,
      label: 'E',
      type: 'end',
    });
  }

  return markers;
}
