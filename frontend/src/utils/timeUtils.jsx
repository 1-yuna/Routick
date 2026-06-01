// 분을 HH:MM 형식으로 변환
export const minutesToTime = (totalMinutes) => {
  const hour = Math.floor(totalMinutes / 60);
  const minute = totalMinutes % 60;
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
};

// 시작 시간(분)과 stayTime으로 time, endTime 계산
export const calcPlaceTimes = (places, startMinute = 9 * 60) => {
  let current = startMinute;
  return places.map((place, index) => {
    const stayTime = Number(place.stayTime) || 0;
    // 다음 장소의 transportTime을 사용
    const nextPlace = places[index + 1];
    const transportTime = Number(nextPlace?.transportTime) || 0;

    const time = minutesToTime(current);
    const endTime = minutesToTime(current + stayTime);
    current += stayTime;
    if (index < places.length - 1) {
      current += transportTime;
    }
    return { ...place, time, endTime, transportTime };
  });
};
