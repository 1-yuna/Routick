package com.routick.domain.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

// 회원가입 요청 (닉네임·비밀번호 형식은 서비스에서 검증 — 전용 에러코드 반환 위해)
public record SignupRequest(
        @NotBlank String nickname,
        @NotBlank @Email String email,
        @NotBlank String password
) {
}