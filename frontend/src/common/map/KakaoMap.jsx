import { useEffect, useRef } from 'react';

export default function KakaoMap({
  lat,
  lng,
  places,
  padding = [50, 50, 50, 50],
  onMarkerClick,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const overlaysRef = useRef([]);
  const polylineRef = useRef(null);

  const placesKey = JSON.stringify(places);

  // 기존 마커/폴리라인 정리
  const clearOverlays = () => {
    overlaysRef.current.forEach((overlay) => overlay.setMap(null));
    overlaysRef.current = [];
    if (polylineRef.current) {
      polylineRef.current.setMap(null);
      polylineRef.current = null;
    }
  };

  useEffect(() => {
    window.__kakaoMarkerClick = (idx) => {
      if (places?.[idx]) onMarkerClick?.(places[idx]);
    };

    window.kakao.maps.load(() => {
      const container = mapContainerRef.current;

      // 지도 인스턴스는 최초 1회만 생성
      if (!mapInstanceRef.current) {
        const initCenter =
          places && places.length > 0
            ? new window.kakao.maps.LatLng(places[0].lat, places[0].lng)
            : new window.kakao.maps.LatLng(lat ?? 37.5665, lng ?? 126.978);

        mapInstanceRef.current = new window.kakao.maps.Map(container, {
          center: initCenter,
          level: places && places.length > 0 ? 4 : 3,
        });
      }

      const map = mapInstanceRef.current;

      // 매번 기존 마커/폴리라인 제거 후 다시 그리기
      clearOverlays();

      if (places && places.length > 0) {
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

          const overlay = new window.kakao.maps.CustomOverlay({
            position,
            content,
            map,
            yAnchor: 0.5,
          });
          overlaysRef.current.push(overlay);
        });

        const polyline = new window.kakao.maps.Polyline({
          path: linePath,
          strokeWeight: 3,
          strokeColor: '#4B5FDC',
          strokeOpacity: 0.8,
          strokeStyle: 'solid',
          map,
        });
        polylineRef.current = polyline;

        map.setBounds(bounds, padding[0], padding[1], padding[2], padding[3]);
      } else if (lat && lng) {
        const position = new window.kakao.maps.LatLng(lat, lng);
        const marker = new window.kakao.maps.Marker({ position, map });
        overlaysRef.current.push(marker);
        map.setCenter(new window.kakao.maps.LatLng(lat - 0.001, lng));
      }
    });

    return () => {
      delete window.__kakaoMarkerClick;
    };
  }, [placesKey, lat, lng]);

  return <div ref={mapContainerRef} className="absolute w-full h-full z-0" />;
}
