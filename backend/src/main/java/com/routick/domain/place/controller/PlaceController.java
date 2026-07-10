package com.routick.domain.place.controller;

import com.routick.domain.place.dto.PlaceDetailResponse;
import com.routick.domain.place.dto.PlaceListResponse;
import com.routick.domain.place.dto.RecommendationResponse;
import com.routick.domain.place.service.PlaceDetailService;
import com.routick.domain.place.service.PlaceListService;
import com.routick.domain.place.service.RecommendationService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/places")
@RequiredArgsConstructor
@Validated
public class PlaceController {

    private final RecommendationService recommendationService;
    private final PlaceListService placeListService;
    private final PlaceDetailService placeDetailService;

    // 지역추천 TOP5 조회
    @GetMapping("/recommendations")
    public ApiResponse<RecommendationResponse> getRecommendations(
            @RequestParam @NotBlank String regionName,
            @RequestParam @NotNull Double lat,
            @RequestParam @NotNull Double lng) {
        return ApiResponse.success(recommendationService.getRecommendations(regionName, lat, lng));
    }

    // 놀거리 카테고리별 조회
    @GetMapping("/list")
    public ApiResponse<PlaceListResponse> getPlaces(
            @RequestParam @NotBlank String category,
            @RequestParam @NotBlank String regionName,
            @RequestParam @NotNull Double lat,
            @RequestParam @NotNull Double lng) {
        return ApiResponse.success(placeListService.getPlaces(category, regionName, lat, lng));
    }

    // 장소 상세 조회 (구체 경로들보다 아래에 선언 — /{placeId}가 마지막)
    @GetMapping("/{placeId}")
    public ApiResponse<PlaceDetailResponse> getPlaceDetail(@PathVariable String placeId) {
        return ApiResponse.success(placeDetailService.getPlaceDetail(placeId));
    }
}