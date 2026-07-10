package com.routick.infra.oauth;

// 소셜 사용자 정보 (카카오/네이버/구글 응답을 공통 형태로 변환한 것)
public record OAuthUserInfo(
        String providerId,      // 소셜 고유 ID
        String email,           // null 가능 (카카오 선택 동의)
        String nickname,        // null 가능
        String profileImageUrl
) {
}