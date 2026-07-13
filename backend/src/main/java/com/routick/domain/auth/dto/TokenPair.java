package com.routick.domain.auth.dto;

// 재발급된 토큰 쌍 (쿠키로만 나가고 body엔 미포함)
public record TokenPair(String accessToken, String refreshToken) {
}