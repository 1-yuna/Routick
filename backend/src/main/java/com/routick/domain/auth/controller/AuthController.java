package com.routick.domain.auth.controller;

import com.routick.domain.auth.dto.EmailSendRequest;
import com.routick.domain.auth.service.AuthService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    // 이메일 인증번호 발송
    @PostMapping("/email/send")
    public ApiResponse<Void> sendEmailCode(@Valid @RequestBody EmailSendRequest request) {
        authService.sendEmailCode(request.email());
        return ApiResponse.success("인증번호가 발송되었습니다.");
    }
}