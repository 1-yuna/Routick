package com.routick.domain.trip.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

// 여행 일정 수정 (전체 교체) 요청
@Getter
@NoArgsConstructor
public class TripDaysUpdateRequest {

    @NotEmpty
    @Valid
    private List<TripCreateRequest.DayDto> days;   // 여행 저장의 days와 동일 구조
}