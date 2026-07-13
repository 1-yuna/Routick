package com.routick.domain.course.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Getter
@NoArgsConstructor
public class PreferenceCreateRequest {

    @NotBlank
    private String routeType;                // only / endpoint

    @NotNull
    @Min(1) @Max(4)
    private Integer travelDays;

    @NotNull
    private LocalDate travelDate;

    @NotBlank
    private String transport;                // walk / car

    private String destination;              // routeType=only 필수 (서비스에서 검증)
    private Double lat;
    private Double lng;

    @Valid
    private List<DayRequest> days;           // routeType=endpoint 필수 (서비스에서 검증)

    @NotBlank
    private String companion;

    private List<String> moods;
    private List<String> activities;
    private List<String> avoidActivities;

    @Getter
    @NoArgsConstructor
    public static class DayRequest {

        @NotNull
        private Integer dayNumber;

        @NotNull
        private Double startLat;
        @NotNull
        private Double startLng;
        private String startName;
        private String startAddress;
        private String startPlaceId;

        private Double midLat;
        private Double midLng;
        private String midName;

        @NotNull
        private Double endLat;
        @NotNull
        private Double endLng;
        private String endName;
        private String endAddress;
        private String endPlaceId;
    }
}