package com.routick.domain.place.service;

import com.routick.domain.place.dto.PlaceDetailResponse;
import com.routick.domain.place.repository.PlaceCacheItemRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// 장소 상세 조회: 놀거리 캐시(place_cache_items)에서 placeId로 조회
@Service
@RequiredArgsConstructor
public class PlaceDetailService {

    private final PlaceCacheItemRepository placeCacheItemRepository;

    @Transactional(readOnly = true)
    public PlaceDetailResponse getPlaceDetail(String placeId) {
        return placeCacheItemRepository.findFirstByPlaceId(placeId)
                .map(PlaceDetailResponse::from)
                .orElseThrow(() -> new CustomException(ErrorCode.PLACE_NOT_FOUND));
    }
}