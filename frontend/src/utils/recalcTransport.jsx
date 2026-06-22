import { getTransportTime } from './directionUtils.jsx';

// blocks 배열을 순회하며:
// 1. place-place 사이에 walk 블록 없으면 자동 삽입
// 2. walk/parking 이동시간 재계산
// 3. placeOrder 재정렬
// transport: 'car' | 'walk'
export async function recalcTransport(blocks, transport) {
  const mode = transport === 'car' ? '자동차' : '도보';

  // 1단계: place-place 사이 walk 블록 삽입
  const withWalk = [];
  for (let i = 0; i < blocks.length; i++) {
    withWalk.push(blocks[i]);

    const cur = blocks[i];
    const next = blocks[i + 1];

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

function getCoord(block) {
  if (!block) return null;
  if (block.lat && block.lng) return { lat: block.lat, lng: block.lng };
  return null;
}
