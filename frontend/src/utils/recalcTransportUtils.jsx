import { getTransportTime } from './directionUtils.jsx';

// blocks 배열을 순회하며:
// 0. 삭제 후 불필요한 walk/taxi/parking 정리
// 1. place-place 사이에 이동(walk/taxi) 블록 없으면 자동 삽입
// 2. walk/taxi/parking 이동시간 재계산
//    *(v3)* 도보 코스에서 도보 20분 초과 구간은 taxi로 자동 전환
//    (백엔드 generate_candidates의 택시 태깅 규칙과 동일 기준)
// 3. placeOrder 재정렬
// transport: 'car' | 'walk'

// 도보 → 택시 전환 기준 (분) — 백엔드 TRAVEL_TIME_LIMIT["도보"]와 동일
const WALK_TAXI_THRESHOLD = 20;

// walk/taxi 공통: 장소-장소 사이 이동 블록인지
const isSegment = (b) => b?.type === 'walk' || b?.type === 'taxi';

export async function recalcTransportUtils(blocks, transport) {
  // 0단계: 타입 전환된 블록의 transport 필드 정규화
  // place→parking: enter/exitTransport 없으면 추가
  // parking→place: enter/exitTransport 제거 (walk로 대체됨)
  const normalized = blocks.map((b) => {
    if (b.type === 'parking') {
      return {
        ...b,
        enterTransport: b.enterTransport ?? {
          mode: transport === 'car' ? 'car' : 'walk',
          minutes: 0,
        },
        exitTransport: b.exitTransport ?? {
          mode: transport === 'car' ? 'car' : 'walk',
          minutes: 0,
        },
      };
    }
    if (b.type === 'place') {
      // place엔 transport 필드 불필요 - 제거
      const { enterTransport, exitTransport, ...rest } = b;
      return rest;
    }
    return b;
  });

  // 1단계: 불필요한 블록 정리
  let cleaned = cleanBlocks(normalized);

  // 1단계: place-place 사이 이동 블록 삽입 (일단 walk로 — 2단계에서 taxi 판정)
  const withWalk = [];
  for (let i = 0; i < cleaned.length; i++) {
    withWalk.push(cleaned[i]);

    const cur = cleaned[i];
    const next = cleaned[i + 1];

    // place 다음에 바로 place가 오면 이동 블록 삽입
    if (cur.type === 'place' && next?.type === 'place') {
      withWalk.push({
        blockOrder: 0, // 나중에 재정렬
        type: 'walk',
        mode: transport === 'car' ? 'car' : 'walk',
        minutes: 0, // 아래에서 계산
      });
    }
  }

  // 2단계: 이동시간 재계산 (차의 위치 추적)
  // hasCar: 현재 사용자가 차를 가지고 있는지
  // - 자동차 코스: 시작 시 차 보유 (true)
  // - 도보 코스: 차 없음 (false)
  let hasCar = transport === 'car';

  for (let i = 0; i < withWalk.length; i++) {
    const cur = withWalk[i];

    // walk/taxi 블록 (장소-장소 사이)
    // 편집으로 거리가 바뀌었을 수 있으므로 walk/taxi 판정도 매번 다시 수행
    if (isSegment(cur)) {
      const prev = withWalk[i - 1];
      const next = withWalk[i + 1];
      if (prev && next && !next._isAnchor) {
        const prevCoord = getCoord(prev);
        const nextCoord = getCoord(next);
        if (prevCoord && nextCoord) {
          const walkMin = await getTransportTime(prevCoord, nextCoord, '도보');

          if (transport === 'walk' && walkMin > WALK_TAXI_THRESHOLD) {
            // *(v3)* 도보 코스에서 도보 20분 초과 → 택시 전환
            // 시간은 카카오 모빌리티(자동차) 기준으로 재계산
            cur.type = 'taxi';
            cur.mode = 'taxi';
            cur.minutes = await getTransportTime(
              prevCoord,
              nextCoord,
              '자동차'
            );
          } else {
            cur.type = 'walk';
            cur.mode = 'walk';
            cur.minutes = walkMin;
          }
        }
      }
    }

    // parking 블록
    if (cur.type === 'parking') {
      const prev = withWalk[i - 1];
      const next = withWalk[i + 1];

      // enterTransport: 주차장으로 진입
      // - 차를 가지고 있으면 자동차로 와서 주차 (hasCar → false)
      // - 차가 없으면 도보로 주차장 가서 차를 뺌 (hasCar → true)
      if (cur.enterTransport && prev) {
        const prevCoord = getCoord(prev);
        const curCoord = { lat: cur.lat, lng: cur.lng };
        if (prevCoord) {
          const enterMode = hasCar ? '자동차' : '도보';
          cur.enterTransport = {
            mode: hasCar ? 'car' : 'walk',
            minutes: await getTransportTime(prevCoord, curCoord, enterMode),
          };
          // 차 보유 → 주차함 / 차 없음 → 차 뺌
          hasCar = !hasCar;
        }
      }

      // exitTransport: 주차장에서 출발
      // - 다음이 주차장이면 차를 빼서 자동차로 이동 (hasCar 유지/획득)
      // - 다음이 장소면 주차하고 도보 이동
      // - 다음이 anchor(end)면 계산 건너뜀 (end.enterTransport가 별도 처리)
      if (cur.exitTransport && next && !next._isAnchor) {
        const curCoord = { lat: cur.lat, lng: cur.lng };
        const nextCoord = getCoord(next);
        if (nextCoord) {
          const goCar = next.type === 'parking';
          const exitMode = goCar ? '자동차' : '도보';
          cur.exitTransport = {
            mode: goCar ? 'car' : 'walk',
            minutes: await getTransportTime(curCoord, nextCoord, exitMode),
          };
          // 다음이 주차장: 차 타고 이동 중 → 다음 주차장에 차 가지고 도착 (hasCar=true)
          // 다음이 장소: 차 주차하고 도보 → hasCar=false
          hasCar = goCar ? true : false;
        }
      }
    }
  }

  // 3단계: blockOrder + placeOrder 재정렬 + 시간 재계산 (시작 09:00 고정)
  let placeCount = 0;
  let current = 9 * 60; // 09:00 (분)

  const toTime = (m) =>
    `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;

  return withWalk.map((block, idx) => {
    const base = { ...block, blockOrder: idx + 1 };

    if (isSegment(block)) {
      current += Number(block.minutes) || 0;
      return base;
    }

    if (block.type === 'parking') {
      current += Number(block.enterTransport?.minutes) || 0;
      const arriveTime = toTime(current);
      current += Number(block.exitTransport?.minutes) || 0;
      const leaveTime = toTime(current);
      return { ...base, arriveTime, leaveTime };
    }

    // place (anchor는 placeCount에서 제외 - 실제 장소가 아님)
    const stay = Number(block.stayMinutes) || 0;
    const arriveTime = toTime(current);
    current += stay;
    const leaveTime = toTime(current);

    if (block._isAnchor) {
      return { ...base, arriveTime, leaveTime };
    }

    placeCount++;
    return { ...base, placeOrder: placeCount, arriveTime, leaveTime };
  });
}

// 삭제 후 불필요한 블록 정리
// - 연속된 walk/taxi → 하나로 합치기
// - 맨 앞 / 맨 뒤 walk/taxi 제거
// - parking 다음에 바로 parking이면 중간 parking의 enterTransport를 앞 parking의 exitTransport로 병합
function cleanBlocks(blocks) {
  let result = [...blocks];

  // 1) 맨 앞 이동 블록 제거
  while (result.length > 0 && isSegment(result[0])) {
    result = result.slice(1);
  }

  // 2) 맨 뒤 이동 블록 제거
  while (result.length > 0 && isSegment(result[result.length - 1])) {
    result = result.slice(0, -1);
  }

  // 3) 연속된 이동 블록 → 하나만 남기기 (walk-taxi 연속 포함)
  const deduped = [];
  for (let i = 0; i < result.length; i++) {
    if (isSegment(result[i]) && isSegment(deduped[deduped.length - 1])) {
      continue; // 연속 이동 블록은 skip
    }
    deduped.push(result[i]);
  }

  return deduped;
}

function getCoord(block) {
  if (!block) return null;
  if (block.lat && block.lng) return { lat: block.lat, lng: block.lng };
  return null;
}
