package com.routick.domain.auth.dto;

// 회원가입 응답
public record SignupResponse(Long id, String nickname, String email) {
}