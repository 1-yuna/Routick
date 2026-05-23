import { useEffect, useRef } from 'react';

export default function KakaoMap({ lat, lng }) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (!window.kakao || !window.kakao.maps) {
      console.error('kakao not loaded');
      return;
    }

    window.kakao.maps.load(() => {
      const container = mapRef.current;

      const markerPosition = new window.kakao.maps.LatLng(lat, lng);

      const options = {
        center: new window.kakao.maps.LatLng(lat - 0.001, lng),
        level: 3,
      };

      const map = new window.kakao.maps.Map(container, options);

      const marker = new window.kakao.maps.Marker({
        position: markerPosition,
      });

      marker.setMap(map);
    });
  }, [lat, lng]);

  return <div ref={mapRef} className="absolute w-full h-full z-0" />;
}
