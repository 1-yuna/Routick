import { useState, useRef, useCallback, useEffect, useMemo } from 'react';

// 드래그로 높이 조절 가능한 바텀시트
// snapPoints: 드래그 종료 시 고정될 높이값 배열
export default function BottomSheet({
  sheetY,
  setSheetY,
  initialHeight,
  snapPoints,
  maxHeightPercent,
  children,
  footer,
}) {
  const contentRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [startHeight, setStartHeight] = useState(initialHeight);
  const [lastY, setLastY] = useState(0);

  // 오름차순 정렬된 스냅 포인트
  const sortedSnapPoints = useMemo(
    () => [...snapPoints].sort((a, b) => a - b),
    [snapPoints]
  );

  // 현재 높이와 가장 가까운 스냅 포인트 반환
  const findNearestSnapPoint = useCallback(
    (height) => {
      let closest = sortedSnapPoints[0];
      sortedSnapPoints.forEach((p) => {
        if (Math.abs(p - height) < Math.abs(closest - height)) closest = p;
      });
      return closest;
    },
    [sortedSnapPoints]
  );

  // 드래그 시작
  const handleDragStart = (e) => {
    const clientY = e.touches?.[0].clientY || e.clientY;
    setIsDragging(true);
    setStartY(clientY);
    setLastY(clientY);
    setStartHeight(sheetY);
  };

  // 드래그 중 - 높이 계산 및 스크롤 충돌 처리
  const handleDragMove = useCallback(
    (e) => {
      if (!isDragging) return;
      const currentY = e.touches?.[0].clientY || e.clientY;
      const deltaFromStart = startY - currentY;

      // 바디가 스크롤 중이면 드래그 중단
      if (contentRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
        const isScrollable = scrollHeight > clientHeight;
        const isAtTop = scrollTop === 0;
        if (isScrollable && !isAtTop && deltaFromStart > 0) {
          setIsDragging(false);
          return;
        }
      }

      const minHeight = sortedSnapPoints[0];
      const maxHeight = (window.innerHeight * maxHeightPercent) / 100;
      const newHeight = Math.max(
        minHeight,
        Math.min(startHeight + deltaFromStart, maxHeight)
      );

      setSheetY(newHeight);
      setLastY(currentY);
    },
    [isDragging, startY, lastY, startHeight, sortedSnapPoints, maxHeightPercent]
  );

  // 드래그 종료 - 가장 가까운 스냅 포인트로 이동
  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);
    setSheetY(findNearestSnapPoint(sheetY));
  }, [isDragging, sheetY, findNearestSnapPoint]);

  // 마우스/터치 이벤트 등록 및 정리
  useEffect(() => {
    window.addEventListener('mousemove', handleDragMove);
    window.addEventListener('mouseup', handleDragEnd);
    window.addEventListener('touchmove', handleDragMove);
    window.addEventListener('touchend', handleDragEnd);
    return () => {
      window.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', handleDragEnd);
      window.removeEventListener('touchmove', handleDragMove);
      window.removeEventListener('touchend', handleDragEnd);
    };
  }, [handleDragMove, handleDragEnd]);

  return (
    <div
      className="z-10 fixed left-0 right-0 bottom-0 bg-default rounded-t-20 shadow-lg transition-all duration-200 flex flex-col"
      style={{ height: `${sheetY}px` }}
    >
      {/*핸들 - 드래그 영역*/}
      <div
        onMouseDown={handleDragStart}
        onTouchStart={handleDragStart}
        className="flex justify-center h-12 w-full pt-3 cursor-grab"
      >
        <div className="w-16 h-[3px] bg-line2 rounded-full" />
      </div>

      {/*바디 - 스크롤 가능한 컨텐츠 영역*/}
      <div
        ref={contentRef}
        className={`px-6 overflow-y-auto flex-1 ${footer ? 'pb-8' : 'pb-[88px]'}`}
      >
        {children}
      </div>

      {/*푸터*/}
      {footer && <div className="px-6 pb-[88px] flex-shrink-0">{footer}</div>}
    </div>
  );
}
