package com.routick.domain.trip.controller;

import com.routick.domain.trip.dto.*;
import com.routick.domain.trip.service.TripService;
import com.routick.global.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/trips")
@RequiredArgsConstructor
@Tag(name = "Trip", description = "내 여행")
public class TripController {

    private final TripService tripService;

    // 여행 저장
    @Operation(summary = "여행 저장", description = "결과 화면에서 편집 반영된 최종 일정을 저장한다")
    @PostMapping
    public ApiResponse<TripCreateResponse> createTrip(@Valid @RequestBody TripCreateRequest request) {
        TripCreateResponse response = tripService.createTrip(request);
        return ApiResponse.success("저장이 완료되었어요!", response);
    }

    // 여행 일정 수정 (전체 교체)
    @Operation(summary = "여행 일정 수정", description = "편집 완료 시 프론트가 재계산한 일정 전체로 교체한다")
    @PutMapping("/{tripId}/days")
    public ApiResponse<Void> updateTripDays(
            @PathVariable Long tripId,
            @Valid @RequestBody TripDaysUpdateRequest request) {
        tripService.updateTripDays(tripId, request);
        return ApiResponse.success("일정이 수정되었습니다.");
    }

    // 내 여행 목록 조회
    @Operation(summary = "내 여행 목록 조회", description = "저장된 여행을 최신순으로 조회한다 (카드용 라벨·태그 포함)")
    @GetMapping
    public ApiResponse<TripListResponse> getTrips() {
        return ApiResponse.success(tripService.getTrips());
    }

    // 내 여행 상세 조회
    @Operation(summary = "내 여행 상세 조회", description = "일자별 타임라인을 코스 생성 응답과 동일한 구조로 조회한다")
    @GetMapping("/{tripId}")
    public ApiResponse<TripDetailResponse> getTripDetail(@PathVariable Long tripId) {
        return ApiResponse.success(tripService.getTripDetail(tripId));
    }

    // 내 여행 수정 (제목·커버)
    @Operation(summary = "여행 수정", description = "제목·커버 이미지를 수정한다 (multipart/form-data)")
    @PatchMapping("/{tripId}")
    public ApiResponse<TripUpdateResponse> updateTrip(
            @PathVariable Long tripId,
            @RequestParam(required = false) String title,
            @RequestParam(required = false) MultipartFile coverImage) {
        return ApiResponse.success("여행이 수정되었습니다.", tripService.updateTrip(tripId, title, coverImage));
    }

    // 내 여행 삭제
    @Operation(summary = "여행 삭제", description = "여행과 하위 일정을 삭제한다")
    @DeleteMapping("/{tripId}")
    public ApiResponse<Void> deleteTrip(@PathVariable Long tripId) {
        tripService.deleteTrip(tripId);
        return ApiResponse.success("여행이 삭제되었습니다.");
    }
}