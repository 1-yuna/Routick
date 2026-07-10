package com.routick.global.util;

import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;

import java.time.Duration;

// httpOnly 토큰 쿠키 설정/만료 (secure는 로컬 http라 false — 배포 시 true)
public class CookieUtil {

    public static void addTokenCookie(HttpServletResponse response, String name, String value, Duration maxAge) {
        ResponseCookie cookie = ResponseCookie.from(name, value)
                .httpOnly(true)
                .secure(false)       // TODO: 배포 시 true
                .sameSite("Lax")
                .path("/")
                .maxAge(maxAge)
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }

    public static void expireTokenCookie(HttpServletResponse response, String name) {
        addTokenCookie(response, name, "", Duration.ZERO);
    }
}