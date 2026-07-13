package com.routick.domain.trip.dto;

import java.time.LocalDateTime;
import java.util.List;

// 내 여행 목록 응답
public record TripListResponse(List<TripSummary> trips) {

    public record TripSummary(
            Long tripId,
            String title,
            String coverImageUrl,
            String regionLabel,      // "홍대" 또는 "홍대 → 부산"
            String transport,        // walk / car
            String periodLabel,      // 당일치기 / 1박2일 ...
            String companionLabel,   // 혼자 / 연인 ...
            List<String> tags,       // 분위기·활동 한국어 라벨 (최대 3개)
            LocalDateTime createdAt
    ) {
    }
}