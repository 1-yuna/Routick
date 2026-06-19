import { useState } from 'react';

const DAYS = ['일', '월', '화', '수', '목', '금', '토'];

const PERIOD_DAYS = {
  day: 1,
  '1n2d': 2,
  '2n3d': 3,
  '3n4d': 4,
};

function isSameDay(a, b) {
  if (!a || !b) return false;
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function isBetween(date, start, end) {
  if (!start || !end) return false;
  return date > start && date < end;
}

function toDateOnly(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function addDays(date, n) {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  return d;
}

export default function DateCalendar({ value, onChange, period }) {
  const today = toDateOnly(new Date());
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());

  const start = value?.start ?? null;
  const end = value?.end ?? null;
  const totalDays = PERIOD_DAYS[period] ?? 1;

  const firstDay = new Date(viewYear, viewMonth, 1).getDay();
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

  const prevMonth = () => {
    if (viewMonth === 0) {
      setViewYear((y) => y - 1);
      setViewMonth(11);
    } else {
      setViewMonth((m) => m - 1);
    }
  };

  const nextMonth = () => {
    if (viewMonth === 11) {
      setViewYear((y) => y + 1);
      setViewMonth(0);
    } else {
      setViewMonth((m) => m + 1);
    }
  };

  const isDisabled = (date) => {
    if (date < today) return true;
    // start 선택 후 end 고르는 단계 — period에 맞는 날짜만 활성화
    if (start && !end && totalDays > 1) {
      const requiredEnd = addDays(start, totalDays - 1);
      return !isSameDay(date, requiredEnd);
    }
    return false;
  };

  const handleDateClick = (date) => {
    if (isDisabled(date)) return;
    if (totalDays === 1) {
      onChange({ start: date, end: null });
      return;
    }
    if (!start || (start && end)) {
      onChange({ start: date, end: null });
    } else {
      onChange({ start, end: date });
    }
  };

  const cells = [
    ...Array(firstDay).fill(null),
    ...Array.from(
      { length: daysInMonth },
      (_, i) => new Date(viewYear, viewMonth, i + 1)
    ),
  ];

  return (
    <div className="flex flex-col gap-6">
      {/*월 네비게이션*/}
      <div className="flex items-center justify-center gap-3">
        <button onClick={prevMonth} className="text-black1 text-14-sb">
          {'<'}
        </button>
        <p className="text-14-sb text-black1">
          {viewYear}년 {viewMonth + 1}월
        </p>
        <button onClick={nextMonth} className="text-black1 text-14-sb">
          {'>'}
        </button>
      </div>

      {/*요일 헤더*/}
      <div className="grid grid-cols-7">
        {DAYS.map((day, i) => (
          <p
            key={day}
            className={`text-center text-12-sb ${i === 0 ? 'text-red' : 'text-gray2'}`}
          >
            {day}
          </p>
        ))}
      </div>

      {/*날짜 그리드*/}
      <div className="grid grid-cols-7 gap-y-6">
        {cells.map((date, idx) => {
          if (!date) return <div key={`empty-${idx}`} />;

          const isStart = isSameDay(date, start);
          const isEnd = isSameDay(date, end);
          const isMid = isBetween(date, start, end);
          const disabled = isDisabled(date);
          const isSunday = date.getDay() === 0;

          return (
            <div
              key={date.toISOString()}
              className="relative flex flex-col items-center py-1"
            >
              {/*범위 하이라이트 레이어*/}
              {isMid && (
                <div className="absolute inset-y-1 left-0 right-0 bg-primaryOpacity" />
              )}
              {isStart && end && (
                <div className="absolute inset-y-1 left-1/2 right-0 bg-primaryOpacity" />
              )}
              {isEnd && (
                <div className="absolute inset-y-1 left-0 right-1/2 bg-primaryOpacity" />
              )}

              <button
                onClick={() => handleDateClick(date)}
                disabled={disabled}
                className="relative w-[47px] h-[28px] flex items-center justify-center"
              >
                <div
                  className={`w-7 h-7 flex items-center justify-center rounded-full text-12-sb
                  ${isStart || isEnd ? 'bg-primary text-white' : ''}
                  ${!isStart && !isEnd && isSunday && !disabled ? 'text-red' : ''}
                  ${!isStart && !isEnd && !disabled && !isSunday ? 'text-black1' : ''}
                  ${disabled && !isStart && !isEnd ? 'text-gray1' : ''}
                `}
                >
                  {date.getDate()}
                </div>
              </button>
              {isStart && (
                <p className="text-10-sb text-primary absolute -bottom-4">
                  가는날
                </p>
              )}
              {isEnd && (
                <p className="text-10-sb text-primary absolute -bottom-4">
                  오는날
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
