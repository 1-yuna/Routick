package com.routick.domain.auth.controller;

import com.routick.domain.auth.dto.TokenPair;
import com.routick.domain.auth.service.OAuthService;
import com.routick.domain.user.entity.enums.Provider;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.util.CookieUtil;
import com.routick.infra.oauth.OAuthApiClient;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.time.Duration;

// 소셜 로그인 (리다이렉트 기반이라 JSON 대신 sendRedirect로 응답)
@RestController
@RequestMapping("/api/v1/auth/oauth")
@RequiredArgsConstructor
public class OAuthController {

    private final OAuthService oAuthService;
    private final OAuthApiClient oAuthApiClient;

    @Value("${front.base-url}")
    private String frontBaseUrl;

    // 소셜 로그인 시작: 해당 소셜의 로그인 페이지로 리다이렉트
    @GetMapping("/{provider}")
    public void redirectToProvider(@PathVariable String provider,
                                   HttpServletResponse response) throws IOException {
        response.sendRedirect(oAuthApiClient.buildAuthorizeUrl(toProvider(provider)));
    }

    // 소셜 콜백: 인가코드로 로그인 처리 후 프론트로 리다이렉트
    @GetMapping("/{provider}/callback")
    public void callback(@PathVariable String provider,
                         @RequestParam(required = false) String code,
                         HttpServletResponse response) throws IOException {
        try {
            if (code == null) {   // 사용자가 동의 화면에서 취소한 경우 등
                throw new CustomException(ErrorCode.OAUTH_FAILED);
            }
            TokenPair tokens = oAuthService.socialLogin(toProvider(provider), code);
            CookieUtil.addTokenCookie(response, "accessToken", tokens.accessToken(), Duration.ofHours(1));
            CookieUtil.addTokenCookie(response, "refreshToken", tokens.refreshToken(), Duration.ofDays(30));
            response.sendRedirect(frontBaseUrl + "/");                              // 성공 → 메인
        } catch (CustomException e) {
            response.sendRedirect(frontBaseUrl + "/login?error=" + e.getErrorCode().name());   // 실패 → 로그인 화면
        }
    }

    // kakao/naver/google → Provider enum
    private Provider toProvider(String provider) {
        try {
            return Provider.valueOf(provider.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new CustomException(ErrorCode.OAUTH_FAILED);
        }
    }
}