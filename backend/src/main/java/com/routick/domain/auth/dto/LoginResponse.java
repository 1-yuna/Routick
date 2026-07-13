package com.routick.domain.auth.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.routick.domain.user.entity.User;

import java.time.LocalDateTime;

// 로그인 응답 (GET /users/me와 동일 구조)
@JsonInclude(JsonInclude.Include.NON_NULL)
public record LoginResponse(
        Long userId,
        String nickname,
        String email,
        String profileImageUrl,
        String provider,
        LastLocation lastLocation,
        LocalDateTime createdAt
) {
    public record LastLocation(String regionName, Double lat, Double lng) {
    }

    public static LoginResponse from(User user) {
        LastLocation location = user.getLastLocationRegionName() == null ? null
                : new LastLocation(user.getLastLocationRegionName(),
                user.getLastLocationLat(), user.getLastLocationLng());
        return new LoginResponse(
                user.getId(), user.getNickname(), user.getEmail(),
                user.getProfileImageUrl(), user.getProvider().name().toLowerCase(),
                location, user.getCreatedAt());
    }
}