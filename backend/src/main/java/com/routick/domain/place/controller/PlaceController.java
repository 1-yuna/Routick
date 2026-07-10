package com.routick.domain.place.controller;

import com.routick.domain.place.dto.RecommendationResponse;
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

    // 지역추천 TOP5 조회
    @GetMapping("/recommendations")
    public ApiResponse<RecommendationResponse> getRecommendations(
            @RequestParam @NotBlank String regionName,
            @RequestParam @NotNull Double lat,
            @RequestParam @NotNull Double lng) {
        return ApiResponse.success(recommendationService.getRecommendations(regionName, lat, lng));
    }
}