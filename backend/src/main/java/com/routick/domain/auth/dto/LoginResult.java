package com.routick.domain.auth.dto;

// 로그인 처리 결과 (토큰은 쿠키로 나가므로 응답 body엔 미포함)
public record LoginResult(String accessToken, String refreshToken, LoginResponse user) {
}