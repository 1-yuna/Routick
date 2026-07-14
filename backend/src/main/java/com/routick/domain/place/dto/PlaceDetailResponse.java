package com.routick.domain.place.dto;

import com.routick.domain.place.entity.PlaceCacheItem;

// 장소 상세 응답 (놀거리 진입 전용 — 코스 결과 장소는 프론트 로컬 데이터로 렌더링)
public record PlaceDetailResponse(
        String placeId,
        String name,
        String address,
        Double lat,
        Double lng,
        String imageUrl,         // null 가능 (플레이스홀더 렌더링)
        String description,      // 상세용 3줄 설명
        String kakaoUrl          // 바로가기 버튼 링크
) {
    private static final String KAKAO_MAP_URL = "https://place.map.kakao.com/";

    public static PlaceDetailResponse from(PlaceCacheItem item) {
        return new PlaceDetailResponse(
                item.getPlaceId(),
                item.getName(),
                item.getAddress(),
                item.getLat(),
                item.getLng(),
                item.getImageUrl(),
                item.getDescription(),
                KAKAO_MAP_URL + item.getPlaceId());
    }
}