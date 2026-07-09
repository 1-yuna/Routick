package com.routick.domain.trip.dto;

// 내 여행 수정 응답
public record TripUpdateResponse(Long tripId, String title, String coverImageUrl) {
}