package com.routick.domain.user.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

// 마지막 위치 저장 요청
public record LocationUpdateRequest(
        @NotBlank String regionName,
        @NotNull Double lat,
        @NotNull Double lng
) {
}