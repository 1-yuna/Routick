package com.routick.domain.trip.controller;

import com.routick.domain.trip.dto.*;
import com.routick.domain.trip.service.TripService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/trips")
@RequiredArgsConstructor
public class TripController {

    private final TripService tripService;

    // 여행 저장
    @PostMapping
    public ApiResponse<TripCreateResponse> createTrip(@Valid @RequestBody TripCreateRequest request) {
        TripCreateResponse response = tripService.createTrip(request);
        return ApiResponse.success("저장이 완료되었어요!", response);
    }

    // 여행 일정 수정 (전체 교체)
    @PutMapping("/{tripId}/days")
    public ApiResponse<Void> updateTripDays(
            @PathVariable Long tripId,
            @Valid @RequestBody TripDaysUpdateRequest request) {
        tripService.updateTripDays(tripId, request);
        return ApiResponse.success("일정이 수정되었습니다.");
    }

    // 내 여행 목록 조회
    @GetMapping
    public ApiResponse<TripListResponse> getTrips() {
        return ApiResponse.success(tripService.getTrips());
    }

    // 내 여행 상세 조회
    @GetMapping("/{tripId}")
    public ApiResponse<TripDetailResponse> getTripDetail(@PathVariable Long tripId) {
        return ApiResponse.success(tripService.getTripDetail(tripId));
    }

    // 내 여행 수정 (제목·커버)
    @PatchMapping("/{tripId}")
    public ApiResponse<TripUpdateResponse> updateTrip(
            @PathVariable Long tripId,
            @RequestParam(required = false) String title,
            @RequestParam(required = false) MultipartFile coverImage) {
        return ApiResponse.success("여행이 수정되었습니다.", tripService.updateTrip(tripId, title, coverImage));
    }

    // 내 여행 삭제
    @DeleteMapping("/{tripId}")
    public ApiResponse<Void> deleteTrip(@PathVariable Long tripId) {
        tripService.deleteTrip(tripId);
        return ApiResponse.success("여행이 삭제되었습니다.");
    }
}