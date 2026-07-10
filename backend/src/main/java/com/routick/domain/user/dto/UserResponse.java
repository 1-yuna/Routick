package com.routick.domain.user.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.routick.domain.user.entity.User;

import java.time.LocalDateTime;

// 내 정보 응답 (로그인 응답과 동일 구조)
@JsonInclude(JsonInclude.Include.NON_NULL)
public record UserResponse(
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

    public static UserResponse from(User user) {
        LastLocation location = user.getLastLocationRegionName() == null ? null
                : new LastLocation(user.getLastLocationRegionName(),
                user.getLastLocationLat(), user.getLastLocationLng());
        return new UserResponse(
                user.getId(), user.getNickname(), user.getEmail(),
                user.getProfileImageUrl(), user.getProvider().name().toLowerCase(),
                location, user.getCreatedAt());
    }
}