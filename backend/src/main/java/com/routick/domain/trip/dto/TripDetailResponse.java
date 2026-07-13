package com.routick.domain.trip.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.List;

// 내 여행 상세 응답 (코스 생성 응답과 동일 구조 + tripId/title/coverImageUrl)
@JsonInclude(JsonInclude.Include.NON_NULL)
public record TripDetailResponse(
        Long tripId,
        String title,
        String coverImageUrl,
        String transport,
        Meta meta,
        String region,
        String startRegion,
        String endRegion,
        List<DayDto> days
) {
    public record Meta(
            String period,
            String date,
            String companion,
            List<String> mood,
            List<String> activity,
            List<String> dislike
    ) {
    }

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record DayDto(
            Integer dayNumber,
            EndpointDto start,
            EndpointDto end,
            List<BlockDto> blocks
    ) {
    }

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record EndpointDto(
            String name,
            String address,
            Double lat,
            Double lng,
            String placeId,
            TransportDto enterTransport,
            TransportDto exitTransport
    ) {
    }

    public record TransportDto(String mode, Integer minutes) {
    }

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record BlockDto(
            Integer blockOrder,
            String type,
            String bucket,
            Integer placeOrder,
            String placeId,
            String name,
            String address,
            Double lat,
            Double lng,
            String imageUrl,
            String status,
            String description,
            Integer stayMinutes,
            Integer minutes,
            String arriveTime,
            String leaveTime,
            TransportDto enterTransport,
            TransportDto exitTransport
    ) {
    }
}