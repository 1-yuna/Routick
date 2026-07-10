package com.routick.domain.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

// 이메일 인증번호 발송 요청
public record EmailSendRequest(@NotBlank @Email String email) {
}