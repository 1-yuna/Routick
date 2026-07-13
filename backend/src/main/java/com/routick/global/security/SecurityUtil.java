package com.routick.global.security;

import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

// 현재 로그인한 사용자 ID 조회 창구 (JwtFilter가 심어둔 값을 꺼냄)
public class SecurityUtil {

    public static Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        // 비로그인(익명) 상태면 principal이 Long이 아님
        if (authentication == null || !(authentication.getPrincipal() instanceof Long userId)) {
            throw new CustomException(ErrorCode.UNAUTHORIZED);
        }
        return userId;
    }
}