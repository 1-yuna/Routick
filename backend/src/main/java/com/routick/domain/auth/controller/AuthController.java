package com.routick.domain.auth.controller;

import com.routick.domain.auth.dto.*;
import com.routick.domain.auth.service.AuthService;
import com.routick.domain.auth.service.EmailService;
import com.routick.global.response.ApiResponse;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.web.bind.annotation.*;

import java.time.Duration;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final EmailService emailService;

    // 이메일 인증번호 발송
    @PostMapping("/email/send")
    public ApiResponse<Void> sendEmailCode(@Valid @RequestBody EmailSendRequest request) {
        emailService.sendEmailCode(request.email());
        return ApiResponse.success("인증번호가 발송되었습니다.");
    }

    // 이메일 인증번호 확인
    @PostMapping("/email/verify")
    public ApiResponse<Void> verifyEmailCode(@Valid @RequestBody EmailVerifyRequest request) {
        emailService.verifyEmailCode(request.email(), request.code());
        return ApiResponse.success("인증이 완료되었습니다.");
    }

    // 회원가입 (201 Created)
    @PostMapping("/signup")
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<SignupResponse> signup(@Valid @RequestBody SignupRequest request) {
        return ApiResponse.success("회원가입이 완료되었습니다.", authService.signup(request));
    }

    // 로그인 — 토큰은 httpOnly 쿠키로 발급
    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request,
                                            HttpServletResponse response) {
        LoginResult result = authService.login(request);
        addTokenCookie(response, "accessToken", result.accessToken(), Duration.ofHours(1));
        addTokenCookie(response, "refreshToken", result.refreshToken(), Duration.ofDays(30));
        return ApiResponse.success("로그인 되었습니다.", result.user());
    }

    // httpOnly 쿠키 설정 (secure는 로컬 http라 false — 배포(HTTPS) 시 true로)
    private void addTokenCookie(HttpServletResponse response, String name, String value, Duration maxAge) {
        ResponseCookie cookie = ResponseCookie.from(name, value)
                .httpOnly(true)      // JS 접근 차단 (XSS 방어)
                .secure(false)       // TODO: 배포 시 true
                .sameSite("Lax")
                .path("/")
                .maxAge(maxAge)
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }
    // 토큰 재발급 (refreshToken 쿠키 사용)
    @PostMapping("/refresh")
    public ApiResponse<Void> refresh(
            @CookieValue(value = "refreshToken", required = false) String refreshToken,
            HttpServletResponse response) {
        TokenPair tokens = authService.reissue(refreshToken);
        addTokenCookie(response, "accessToken", tokens.accessToken(), Duration.ofHours(1));
        addTokenCookie(response, "refreshToken", tokens.refreshToken(), Duration.ofDays(30));
        return ApiResponse.success("토큰이 재발급되었습니다.");
    }

    // 로그아웃: Redis 토큰 삭제 + 쿠키 만료
    @PostMapping("/logout")
    public ApiResponse<Void> logout(
            @CookieValue(value = "refreshToken", required = false) String refreshToken,
            HttpServletResponse response) {
        authService.logout(refreshToken);
        expireTokenCookie(response, "accessToken");
        expireTokenCookie(response, "refreshToken");
        return ApiResponse.success("로그아웃 되었습니다.");
    }

    // 쿠키 즉시 만료 (maxAge=0으로 덮어쓰면 브라우저가 삭제)
    private void expireTokenCookie(HttpServletResponse response, String name) {
        ResponseCookie cookie = ResponseCookie.from(name, "")
                .httpOnly(true)
                .secure(false)       // TODO: 배포 시 true
                .sameSite("Lax")
                .path("/")
                .maxAge(0)
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }
}