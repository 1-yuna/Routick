package com.routick.global.security;

// 현재 로그인한 사용자 ID 조회 창구
// TODO: JWT 구현 시 SecurityContext에서 꺼내도록 이 메서드만 수정
public class SecurityUtil {

    public static Long getCurrentUserId() {
        return 1L;   // 개발 초기: 더미 유저 고정
    }
}