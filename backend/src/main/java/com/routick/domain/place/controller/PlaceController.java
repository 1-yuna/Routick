package com.routick.domain.place.controller;

import com.routick.domain.place.dto.PlaceDetailResponse;
import com.routick.domain.place.dto.PlaceListResponse;
import com.routick.domain.place.dto.RecommendationResponse;
import com.routick.domain.place.service.PlaceDetailService;
import com.routick.domain.place.service.PlaceListService;
import com.routick.domain.place.service.RecommendationService;
import com.routick.global.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/places")
@RequiredArgsConstructor
@Validated
@Tag(name = "Place", description = "홈 (지역추천·놀거리·장소 상세)")
public class PlaceController {

    private final RecommendationService recommendationService;
    private final PlaceListService placeListService;
    private final PlaceDetailService placeDetailService;

    // 지역추천 TOP5 조회
    @Operation(summary = "지역추천 TOP5 조회", description = "블로그 트렌드 기반 지역 명물 5곳 (30일 캐시)")
    @GetMapping("/recommendations")
    public ApiResponse<RecommendationResponse> getRecommendations(
            @RequestParam @NotBlank String regionName,
            @RequestParam @NotNull Double lat,
            @RequestParam @NotNull Double lng) {
        return ApiResponse.success(recommendationService.getRecommendations(regionName, lat, lng));
    }

    // 놀거리 카테고리별 조회
    @Operation(summary = "놀거리 카테고리별 조회", description = "HOTPLACE/FOOD_CAFE/CULTURE_NATURE별 인기순 10곳 (30일 캐시)")
    @GetMapping("/list")
    public ApiResponse<PlaceListResponse> getPlaces(
            @RequestParam @NotBlank String category,
            @RequestParam @NotBlank String regionName,
            @RequestParam @NotNull Double lat,
            @RequestParam @NotNull Double lng) {
        return ApiResponse.success(placeListService.getPlaces(category, regionName, lat, lng));
    }

    // 장소 상세 조회 (구체 경로들보다 아래에 선언 — /{placeId}가 마지막)
    @Operation(summary = "장소 상세 조회", description = "놀거리 카드 클릭 시 상세 정보 + 카카오맵 바로가기 링크")
    @GetMapping("/{placeId}")
    public ApiResponse<PlaceDetailResponse> getPlaceDetail(@PathVariable String placeId) {
        return ApiResponse.success(placeDetailService.getPlaceDetail(placeId));
    }
}