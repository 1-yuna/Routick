package com.routick.domain.auth.service;

import com.routick.domain.auth.dto.TokenPair;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.jwt.JwtProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

// 토큰 발급·재발급·무효화 전담 (refreshToken의 Redis 관리 포함)
@Service
@RequiredArgsConstructor
public class TokenService {

    private static final Duration REFRESH_TTL = Duration.ofDays(30);
    private static final String REFRESH_KEY_PREFIX = "refresh:";

    private final JwtProvider jwtProvider;
    private final StringRedisTemplate redisTemplate;

    // 토큰 쌍 발급 + refreshToken Redis 저장 (로그인·소셜 로그인 공용)
    public TokenPair issue(Long userId) {
        String accessToken = jwtProvider.createAccessToken(userId);
        String refreshToken = jwtProvider.createRefreshToken(userId);
        redisTemplate.opsForValue().set(REFRESH_KEY_PREFIX + userId, refreshToken, REFRESH_TTL);
        return new TokenPair(accessToken, refreshToken);
    }

    // 토큰 재발급 (RTR: refreshToken도 함께 교체)
    public TokenPair reissue(String refreshToken) {
        // 쿠키 자체가 없음
        if (refreshToken == null) {
            throw new CustomException(ErrorCode.INVALID_REFRESH_TOKEN);
        }

        // 서명·만료 검증 + userId 추출
        Long userId;
        try {
            userId = jwtProvider.getUserId(refreshToken);
        } catch (Exception e) {
            throw new CustomException(ErrorCode.INVALID_REFRESH_TOKEN);
        }

        // Redis에 저장된 토큰과 대조 (로그아웃·강제만료·탈취 대응)
        String savedToken = redisTemplate.opsForValue().get(REFRESH_KEY_PREFIX + userId);
        if (!refreshToken.equals(savedToken)) {
            throw new CustomException(ErrorCode.INVALID_REFRESH_TOKEN);
        }

        // 새 토큰 쌍 발급 + Redis 갱신 (이전 refreshToken은 즉시 무효화)
        return issue(userId);
    }

    // 토큰 무효화 (로그아웃)
    public void logout(String refreshToken) {
        if (refreshToken == null) return;
        try {
            Long userId = jwtProvider.getUserId(refreshToken);
            redisTemplate.delete(REFRESH_KEY_PREFIX + userId);
        } catch (Exception ignored) {
            // 이미 만료·위조된 토큰이면 지울 것도 없음 → 조용히 통과
        }
    }
}