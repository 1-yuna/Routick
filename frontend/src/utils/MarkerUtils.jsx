// bucket별 마커 색상
const BUCKET_COLOR = {
  food: '#FF8A5C',
  cafe: '#4B5FDC',
  activity: '#4B5FDC',
  other: '#4B5FDC',
};

// blocks 배열에서 지도에 표시할 마커 목록 추출
// - place: bucket별 색상 + placeOrder 번호
// - parking: 연속된 parking 그룹의 마지막 parking만 표시 (주황색 P 마커)
export function extractMarkers(blocks) {
  const markers = [];
  let i = 0;

  while (i < blocks.length) {
    const block = blocks[i];

    if (block.type === 'place') {
      markers.push({
        lat: block.lat,
        lng: block.lng,
        color: BUCKET_COLOR[block.bucket] ?? '#4B5FDC',
        label: String(block.placeOrder),
        type: 'place',
      });
    } else if (block.type === 'parking') {
      // 연속된 parking 그룹의 마지막 parking 찾기
      let last = block;
      while (i + 1 < blocks.length && blocks[i + 1].type === 'parking') {
        i++;
        last = blocks[i];
      }
      markers.push({
        lat: last.lat,
        lng: last.lng,
        color: '#FFB705',
        label: 'P',
        type: 'parking',
      });
    }

    i++;
  }

  return markers;
}
