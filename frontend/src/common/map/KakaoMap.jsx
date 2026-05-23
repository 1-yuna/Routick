import { useEffect, useRef } from 'react';

export default function KakaoMap() {
  const mapRef = useRef(null);

  useEffect(() => {
    console.log('kakao check:', window.kakao);

    if (!window.kakao || !window.kakao.maps) {
      console.error('kakao not loaded');
      return;
    }

    window.kakao.maps.load(() => {
      const container = mapRef.current;

      const markerPosition = new window.kakao.maps.LatLng(37.5665, 126.978);

      const options = {
        center: new window.kakao.maps.LatLng(37.5655, 126.978), // 중심점을 마커보다 아래로
        level: 3,
      };

      const map = new window.kakao.maps.Map(container, options);

      const marker = new window.kakao.maps.Marker({
        position: markerPosition,
      });

      marker.setMap(map);
    });
  }, []);

  return <div ref={mapRef} className="absolute w-full h-full z-0" />;
}
