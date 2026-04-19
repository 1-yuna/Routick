import { useState, useRef, useCallback, useEffect } from "react";

// 바텀 시트
export default function BottomSheet({
                                        initialHeight,
                                        snapPoints,
                                        maxHeightPercent,
                                        children,
                                    }) {
    const contentRef = useRef(null);

    const [sheetHeight, setSheetHeight] = useState(initialHeight);
    const [isDragging, setIsDragging] = useState(false);
    const [startY, setStartY] = useState(0);
    const [startHeight, setStartHeight] = useState(initialHeight);
    const [currentSnapIndex, setCurrentSnapIndex] = useState(0);
    const [dragDirection, setDragDirection] = useState(0);
    const [lastY, setLastY] = useState(0);

    // 방향 감지 민감도
    const sensitivity = 1;

    // snap 정렬
    const calculateSnapPoints = () => {
        return [...snapPoints].sort((a, b) => a - b);
    };

    // 가장 가까운 snap point 찾기
    const findNearestSnapPoint = (height) => {
        const points = calculateSnapPoints();

        let closest = points[0];
        let index = 0;

        // 현재 높이와 가장 가까운 값 찾기
        points.forEach((p, i) => {
            if (Math.abs(p - height) < Math.abs(closest - height)) {
                closest = p;
                index = i;
            }
        });

        return { point: closest, index };
    };

    // 드래그 시작
    const handleDragStart = (e) => {
        const clientY = e.touches?.[0].clientY || e.clientY;

        setIsDragging(true);
        setStartY(clientY);
        setLastY(clientY);
        setStartHeight(sheetHeight);
    };

    // 드래그 중
    const handleDragMove = useCallback(
        (e) => {
            if (!isDragging) return;

            const currentY = e.touches?.[0].clientY || e.clientY;

            const deltaFromStart = startY - currentY;
            const deltaFromLast = lastY - currentY;

            // 방향 감지
            if (Math.abs(deltaFromLast) > sensitivity) {
                setDragDirection(deltaFromLast > 0 ? 1 : -1);
            }

            // 스크롤 충돌 방지
            if (contentRef.current) {
                const { scrollTop, scrollHeight, clientHeight } =
                    contentRef.current;

                const isScrollable = scrollHeight > clientHeight;
                const isAtTop = scrollTop === 0;

                if (isScrollable && !isAtTop && deltaFromStart > 0) {
                    setIsDragging(false);
                    return;
                }
            }

            // 높이 계산
            const points = calculateSnapPoints();
            const minHeight = points[0];
            const maxHeight = (window.innerHeight * maxHeightPercent) / 100;

            const newHeight = Math.max(
                minHeight,
                Math.min(startHeight + deltaFromStart, maxHeight)
            );

            setSheetHeight(newHeight);
            setLastY(currentY);
        },
        [isDragging, startY, lastY, startHeight]
    );

    // 드래그 종료
    const handleDragEnd = useCallback(() => {
        if (!isDragging) return;

        setIsDragging(false);

        const { point, index } = findNearestSnapPoint(sheetHeight);

        setSheetHeight(point);
        setCurrentSnapIndex(index);
        setDragDirection(0);
    }, [isDragging, sheetHeight]);

    // 이벤트 바인딩
    useEffect(() => {
        window.addEventListener("mousemove", handleDragMove);
        window.addEventListener("mouseup", handleDragEnd);
        window.addEventListener("touchmove", handleDragMove);
        window.addEventListener("touchend", handleDragEnd);

        return () => {
            window.removeEventListener("mousemove", handleDragMove);
            window.removeEventListener("mouseup", handleDragEnd);
            window.removeEventListener("touchmove", handleDragMove);
            window.removeEventListener("touchend", handleDragEnd);
        };
    }, [handleDragMove, handleDragEnd]);

    return (
        <div
            className="fixed left-0 right-0 bottom-0 bg-white rounded-t-2xl shadow-xl transition-all duration-200"
            style={{
                height: `${sheetHeight}px`,
            }}
        >
            {/* 핸들 */}
            <div
                onMouseDown={handleDragStart}
                onTouchStart={handleDragStart}
                className="flex justify-center py-3 cursor-grab"
            >
                <div className="w-10 h-1.5 bg-gray-300 rounded-full" />
            </div>

            {/* 콘텐츠 */}
            <div
                ref={contentRef}
                className="px-5 pb-10 overflow-y-auto h-full"
            >
                {children}
            </div>
        </div>
    );
}