// Map 컨테이너
// 바텀시트의 높이 값을 반영
export default function MapContainer({ sheetY, children }) {
    return (
        <div
            style={{
                height: `calc(100vh - ${sheetY}px)`,
                transition: "height 0.2s ease",
            }}
        >
            {children}
        </div>
    );
}