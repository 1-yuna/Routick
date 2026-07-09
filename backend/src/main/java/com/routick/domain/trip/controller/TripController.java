package com.routick.domain.trip.controller;

import com.routick.domain.trip.dto.TripCreateRequest;
import com.routick.domain.trip.dto.TripCreateResponse;
import com.routick.domain.trip.dto.TripDaysUpdateRequest;
import com.routick.domain.trip.service.TripService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

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
}