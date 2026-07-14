package com.routick.domain.trip.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class TripCreateRequest {

    @NotNull
    private Long preferenceId;

    @NotBlank
    private String title;

    private String coverImageUrl;      // 미입력 시 첫 place 이미지

    @NotBlank
    private String transport;          // walk / car

    private String region;             // routeType=only
    private String startRegion;        // routeType=endpoint
    private String endRegion;

    @NotEmpty
    @Valid
    private List<DayDto> days;

    @Getter
    @NoArgsConstructor
    public static class DayDto {
        @NotNull
        private Integer dayNumber;
        private EndpointDto start;     // endpoint만
        private EndpointDto end;
        @NotEmpty
        @Valid
        private List<BlockDto> blocks;
    }

    @Getter
    @NoArgsConstructor
    public static class EndpointDto {
        private String name;
        private String address;
        private Double lat;
        private Double lng;
        private String placeId;
        private TransportDto enterTransport;
        private TransportDto exitTransport;
    }

    @Getter
    @NoArgsConstructor
    public static class TransportDto {
        private String mode;
        private Integer minutes;
    }

    @Getter
    @NoArgsConstructor
    public static class BlockDto {
        @NotNull
        private Integer blockOrder;
        @NotBlank
        private String type;           // place / walk / parking
        private String bucket;
        private Integer placeOrder;
        private String placeId;
        private String name;
        private String address;
        private Double lat;
        private Double lng;
        private String imageUrl;
        private String imageData;      // 로컬에서 새로 첨부한 이미지 (data URL, base64) - 있으면 저장 후 imageUrl을 덮어씀
        private String status;
        private String description;
        private Integer stayMinutes;
        private Integer minutes;       // walk만
        private String arriveTime;     // HH:mm
        private String leaveTime;
        private TransportDto enterTransport;   // parking만
        private TransportDto exitTransport;
    }
}