import { useEffect, useRef } from 'react';

// 카테고리별 마커 색상
const CATEGORY_COLOR = {
  food: '#FFB705',
  lodging: '#229EBC',
};

// 카카오맵 컴포넌트
// - places 있으면: 다중 마커 + 동선 표시 (ResultPage)
// - places 없으면: 단일 마커 (PlaceDetailPage)
export default function KakaoMap({
  lat,
  lng,
  places,
  padding = [50, 50, 50, 50],
}) {
  const mapRef = useRef(null);
  useEffect(() => {
    window.kakao.maps.load(() => {
      const container = mapRef.current;

      // places 있으면 다중 마커, 없으면 단일 마커
      if (places && places.length > 0) {
        const map = new window.kakao.maps.Map(container, {
          center: new window.kakao.maps.LatLng(places[0].lat, places[0].lng),
          level: 4,
        });

        const bounds = new window.kakao.maps.LatLngBounds();
        const linePath = [];

        places.forEach((place, index) => {
          const position = new window.kakao.maps.LatLng(place.lat, place.lng);
          bounds.extend(position);
          linePath.push(position);

          // 카테고리 색상 적용한 번호 마커
          const color = CATEGORY_COLOR[place.category] || '#4B5FDC';
          const content = `<div style="width:24px;height:24px;background:${color};border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:600;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.2);">${index + 1}</div>`;

          new window.kakao.maps.CustomOverlay({
            position,
            content,
            map,
            yAnchor: 0.5,
          });
        });

        // 장소 간 동선 표시
        new window.kakao.maps.Polyline({
          path: linePath,
          strokeWeight: 3,
          strokeColor: '#4B5FDC',
          strokeOpacity: 0.8,
          strokeStyle: 'solid',
          map,
        });

        // 모든 마커가 보이도록 지도 범위 조정
        map.setBounds(bounds, padding[0], padding[1], padding[2], padding[3]);
      } else {
        // 단일 마커 - 마커보다 약간 위를 중심으로 표시
        const position = new window.kakao.maps.LatLng(lat, lng);
        const map = new window.kakao.maps.Map(container, {
          center: new window.kakao.maps.LatLng(lat - 0.001, lng),
          level: 3,
        });
        new window.kakao.maps.Marker({ position, map });
      }
    });
  }, [lat, lng, places]);

  return <div ref={mapRef} className="absolute w-full h-full z-0" />;
}
