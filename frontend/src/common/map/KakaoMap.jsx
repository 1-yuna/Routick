import { useEffect, useRef } from 'react';

export default function KakaoMap({
  lat,
  lng,
  places,
  padding = [50, 50, 50, 50],
  onMarkerClick,
}) {
  const mapRef = useRef(null);
  const placesKey = JSON.stringify(places);

  useEffect(() => {
    // 지도 렌더링 전에 콜백 먼저 등록
    window.__kakaoMarkerClick = (idx) => {
      if (places?.[idx]) onMarkerClick?.(places[idx]);
    };

    window.kakao.maps.load(() => {
      const container = mapRef.current;

      if (places && places.length > 0) {
        const map = new window.kakao.maps.Map(container, {
          center: new window.kakao.maps.LatLng(places[0].lat, places[0].lng),
          level: 4,
        });

        const bounds = new window.kakao.maps.LatLngBounds();
        const linePath = [];

        places.forEach((place, idx) => {
          const position = new window.kakao.maps.LatLng(place.lat, place.lng);
          bounds.extend(position);
          linePath.push(position);

          const content = `
            <div
              onclick="window.__kakaoMarkerClick(${idx})"
              style="
                width: 24px;
                height: 24px;
                background: ${place.color};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 11px;
                font-weight: 600;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                cursor: pointer;
              ">${place.label ?? ''}</div>
          `;

          new window.kakao.maps.CustomOverlay({
            position,
            content,
            map,
            yAnchor: 0.5,
          });
        });

        new window.kakao.maps.Polyline({
          path: linePath,
          strokeWeight: 3,
          strokeColor: '#4B5FDC',
          strokeOpacity: 0.8,
          strokeStyle: 'solid',
          map,
        });

        map.setBounds(bounds, padding[0], padding[1], padding[2], padding[3]);
      } else {
        const position = new window.kakao.maps.LatLng(lat, lng);
        const map = new window.kakao.maps.Map(container, {
          center: new window.kakao.maps.LatLng(lat - 0.001, lng),
          level: 3,
        });
        new window.kakao.maps.Marker({ position, map });
      }
    });

    return () => {
      delete window.__kakaoMarkerClick;
    };
  }, [placesKey, lat, lng]);

  return <div ref={mapRef} className="absolute w-full h-full z-0" />;
}
