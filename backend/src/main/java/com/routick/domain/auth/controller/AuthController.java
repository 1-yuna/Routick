package com.routick.domain.auth.controller;

import com.routick.domain.auth.dto.EmailSendRequest;
import com.routick.domain.auth.dto.EmailVerifyRequest;
import com.routick.domain.auth.dto.SignupRequest;
import com.routick.domain.auth.dto.SignupResponse;
import com.routick.domain.auth.service.AuthService;
import com.routick.domain.auth.service.EmailService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

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
}