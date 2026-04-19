import { useEffect, useRef } from "react";

export default function KakaoMap() {
    const mapRef = useRef(null);

    useEffect(() => {
        console.log("kakao check:", window.kakao);

        if (!window.kakao || !window.kakao.maps) {
            console.error("kakao not loaded");
            return;
        }

        window.kakao.maps.load(() => {
            const container = mapRef.current;

            const options = {
                center: new window.kakao.maps.LatLng(37.5665, 126.9780),
                level: 3,
            };

            const map = new window.kakao.maps.Map(container, options);

            const marker = new window.kakao.maps.Marker({
                position: options.center,
            });

            marker.setMap(map);
        });
    }, []);

    return <div ref={mapRef} className="w-full h-full" />;
}