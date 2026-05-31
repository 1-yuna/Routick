import { useState, useRef, useCallback, useEffect, useMemo } from 'react';

export default function BottomSheet({
  sheetY,
  setSheetY,
  initialHeight,
  snapPoints,
  maxHeightPercent,
  children,
}) {
  const contentRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [startHeight, setStartHeight] = useState(initialHeight);
  const [lastY, setLastY] = useState(0);

  const sensitivity = 1;

  const sortedSnapPoints = useMemo(
    () => [...snapPoints].sort((a, b) => a - b),
    [snapPoints]
  );

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

  const handleDragStart = (e) => {
    const clientY = e.touches?.[0].clientY || e.clientY;
    setIsDragging(true);
    setStartY(clientY);
    setLastY(clientY);
    setStartHeight(sheetY);
  };

  const handleDragMove = useCallback(
    (e) => {
      if (!isDragging) return;
      const currentY = e.touches?.[0].clientY || e.clientY;
      const deltaFromStart = startY - currentY;

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

  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);
    setSheetY(findNearestSnapPoint(sheetY));
  }, [isDragging, sheetY, findNearestSnapPoint]);

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
      className="z-10 fixed left-0 right-0 bottom-0 bg-white rounded-t-2xl shadow-xl transition-all duration-200"
      style={{ height: `${sheetY}px` }}
    >
      {/*핸들*/}
      <div
        onMouseDown={handleDragStart}
        onTouchStart={handleDragStart}
        className="flex justify-center py-3 cursor-grab"
      >
        <div className="w-10 h-1.5 bg-gray-300 rounded-full mb-4" />
      </div>

      {/*바디*/}
      <div ref={contentRef} className="px-6 pb-36 overflow-y-auto h-full">
        {children}
      </div>
    </div>
  );
}
