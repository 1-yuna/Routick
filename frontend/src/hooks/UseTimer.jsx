import { useEffect, useState } from 'react';

// 카운트다운 타이머 훅
// initial: 시작 시간(초), active: 타이머 활성화 여부
export default function useTimer(initial = 120, active) {
  const [time, setTime] = useState(initial);

  useEffect(() => {
    // active가 false면 타이머 실행 안 함
    if (!active) return;

    const timer = setInterval(() => {
      setTime((prev) => {
        // 0이 되면 타이머 종료
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // 컴포넌트 언마운트 or active 변경 시 타이머 정리
    return () => clearInterval(timer);
  }, [active]);

  // 타이머 초기화
  const reset = () => setTime(initial);

  return { time, setTime, reset };
}
