import { getTransportTime } from './directionUtils.jsx';

// blocks 배열을 순회하며:
// 0. 삭제 후 불필요한 walk/parking 정리
// 1. place-place 사이에 walk 블록 없으면 자동 삽입
// 2. walk/parking 이동시간 재계산
// 3. placeOrder 재정렬
// transport: 'car' | 'walk'
export async function recalcTransportUtils(blocks, transport) {
  const mode = transport === 'car' ? '자동차' : '도보';

  // 0단계: 삭제 후 불필요한 블록 정리
  let cleaned = cleanBlocks(blocks);

  // 1단계: place-place 사이 walk 블록 삽입
  const withWalk = [];
  for (let i = 0; i < cleaned.length; i++) {
    withWalk.push(cleaned[i]);

    const cur = cleaned[i];
    const next = cleaned[i + 1];

    // place 다음에 바로 place가 오면 walk 삽입
    if (cur.type === 'place' && next?.type === 'place') {
      withWalk.push({
        blockOrder: 0, // 나중에 재정렬
        type: 'walk',
        mode: transport === 'car' ? 'car' : 'walk',
        minutes: 0, // 아래에서 계산
      });
    }
  }

  // 2단계: 이동시간 재계산
  for (let i = 0; i < withWalk.length; i++) {
    const cur = withWalk[i];

    // walk 블록
    if (cur.type === 'walk') {
      const prev = withWalk[i - 1];
      const next = withWalk[i + 1];
      if (prev && next) {
        const prevCoord = getCoord(prev);
        const nextCoord = getCoord(next);
        if (prevCoord && nextCoord) {
          cur.minutes = await getTransportTime(prevCoord, nextCoord, mode);
        }
      }
    }

    // parking 블록
    if (cur.type === 'parking') {
      const prev = withWalk[i - 1];
      const next = withWalk[i + 1];

      // enterTransport
      if (cur.enterTransport && prev) {
        const prevCoord = getCoord(prev);
        const curCoord = { lat: cur.lat, lng: cur.lng };
        if (prevCoord) {
          const enterMode =
            cur.enterTransport.mode === 'car' ? '자동차' : '도보';
          cur.enterTransport = {
            ...cur.enterTransport,
            minutes: await getTransportTime(prevCoord, curCoord, enterMode),
          };
        }
      }

      // exitTransport
      if (cur.exitTransport && next) {
        const curCoord = { lat: cur.lat, lng: cur.lng };
        const nextCoord = getCoord(next);
        if (nextCoord) {
          const exitMode = cur.exitTransport.mode === 'car' ? '자동차' : '도보';
          cur.exitTransport = {
            ...cur.exitTransport,
            minutes: await getTransportTime(curCoord, nextCoord, exitMode),
          };
        }
      }
    }
  }

  // 3단계: blockOrder + placeOrder 재정렬
  let placeCount = 0;
  return withWalk.map((block, idx) => {
    if (block.type === 'place') placeCount++;
    return {
      ...block,
      blockOrder: idx + 1,
      ...(block.type === 'place' ? { placeOrder: placeCount } : {}),
    };
  });
}

// 삭제 후 불필요한 블록 정리
// - 연속된 walk → 하나로 합치기
// - 맨 앞 / 맨 뒤 walk 제거
// - parking 다음에 바로 parking이면 중간 parking의 enterTransport를 앞 parking의 exitTransport로 병합
function cleanBlocks(blocks) {
  let result = [...blocks];

  // 1) 맨 앞 walk 제거
  while (result.length > 0 && result[0].type === 'walk') {
    result = result.slice(1);
  }

  // 2) 맨 뒤 walk 제거
  while (result.length > 0 && result[result.length - 1].type === 'walk') {
    result = result.slice(0, -1);
  }

  // 3) 연속된 walk → 하나만 남기기
  const deduped = [];
  for (let i = 0; i < result.length; i++) {
    if (
      result[i].type === 'walk' &&
      deduped[deduped.length - 1]?.type === 'walk'
    ) {
      continue; // 연속 walk는 skip
    }
    deduped.push(result[i]);
  }

  // 4) parking 다음 parking: 앞 parking의 exitTransport를 뒤 parking으로 이전
  //    (장소가 삭제되어 주차장끼리 붙은 경우 이동시간 병합)
  const merged = [];
  for (let i = 0; i < deduped.length; i++) {
    const cur = deduped[i];
    const prev = merged[merged.length - 1];

    if (cur.type === 'parking' && prev?.type === 'parking') {
      // 앞 parking의 exitTransport → 뒤 parking의 exitTransport로 이전
      // (앞 parking은 출차 역할을 잃음 → enterTransport/exitTransport 제거)
      const updatedPrev = { ...prev };
      delete updatedPrev.exitTransport;
      merged[merged.length - 1] = updatedPrev;

      // 뒤 parking은 앞 parking의 exitTransport를 이어받아 표시
      merged.push({
        ...cur,
        enterTransport: prev.exitTransport ?? cur.enterTransport,
      });
    } else {
      merged.push(cur);
    }
  }

  return merged;
}

function getCoord(block) {
  if (!block) return null;
  if (block.lat && block.lng) return { lat: block.lat, lng: block.lng };
  return null;
}
