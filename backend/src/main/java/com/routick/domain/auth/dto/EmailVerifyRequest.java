package com.routick.domain.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

// 이메일 인증번호 확인 요청
public record EmailVerifyRequest(
        @NotBlank @Email String email,
        @NotBlank String code
) {
}