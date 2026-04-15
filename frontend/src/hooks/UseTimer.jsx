import { useEffect, useState } from "react";

export default function useTimer(initial = 120, active) {
  const [time, setTime] = useState(initial);

  useEffect(() => {
    if (!active) return;

    const timer = setInterval(() => {
      setTime((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [active]);

  const reset = () => setTime(initial);

  return { time, setTime, reset };
}