package com.routick.global.jwt;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

// JWT 생성·검증 담당
@Component
public class JwtProvider {

    private final SecretKey key;
    private final long accessExpirationMs;
    private final long refreshExpirationMs;

    public JwtProvider(@Value("${jwt.secret}") String secret,
                       @Value("${jwt.access-expiration-ms}") long accessExpirationMs,
                       @Value("${jwt.refresh-expiration-ms}") long refreshExpirationMs) {
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
        this.accessExpirationMs = accessExpirationMs;
        this.refreshExpirationMs = refreshExpirationMs;
    }

    public String createAccessToken(Long userId) {
        return createToken(userId, accessExpirationMs);
    }

    public String createRefreshToken(Long userId) {
        return createToken(userId, refreshExpirationMs);
    }

    // 토큰에서 userId 추출 (서명·만료 검증 포함, 실패 시 JwtException 발생)
    public Long getUserId(String token) {
        String subject = Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload()
                .getSubject();
        return Long.valueOf(subject);
    }

    private String createToken(Long userId, long expirationMs) {
        Date now = new Date();
        return Jwts.builder()
                .subject(String.valueOf(userId))     // 토큰 주인
                .issuedAt(now)
                .expiration(new Date(now.getTime() + expirationMs))
                .signWith(key)
                .compact();
    }
}