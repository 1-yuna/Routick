package com.routick.domain.auth.service;

import com.routick.domain.auth.dto.SignupRequest;
import com.routick.domain.auth.dto.SignupResponse;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.entity.enums.Provider;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.regex.Pattern;

// 계정 관련: 회원가입 (추후 로그인·토큰 재발급·로그아웃 추가 예정)
@Service
@RequiredArgsConstructor
public class AuthService {

    // 비밀번호: 8자 이상, 영문+숫자 포함
    private static final Pattern PASSWORD_PATTERN =
            Pattern.compile("^(?=.*[A-Za-z])(?=.*\\d).{8,}$");

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    // 회원가입
    @Transactional
    public SignupResponse signup(SignupRequest request) {
        // 형식 검증 (전용 에러코드)
        if (request.nickname().length() < 2 || request.nickname().length() > 10) {
            throw new CustomException(ErrorCode.INVALID_NICKNAME);
        }
        if (!PASSWORD_PATTERN.matcher(request.password()).matches()) {
            throw new CustomException(ErrorCode.INVALID_PASSWORD_FORMAT);
        }

        // 이메일 인증 완료 확인
        if (!emailService.isVerified(request.email())) {
            throw new CustomException(ErrorCode.EMAIL_NOT_VERIFIED);
        }

        // 중복 가입 방지 (인증~가입 사이에 다른 요청으로 가입됐을 수 있음)
        if (userRepository.findByEmail(request.email()).isPresent()) {
            throw new CustomException(ErrorCode.EMAIL_ALREADY_EXISTS);
        }

        // 사용자 생성 (비밀번호는 BCrypt 암호화)
        User user = User.builder()
                .nickname(request.nickname())
                .email(request.email())
                .password(passwordEncoder.encode(request.password()))
                .provider(Provider.EMAIL)
                .build();
        userRepository.save(user);

        // 인증 플래그 제거 (일회용)
        emailService.consumeVerified(request.email());

        return new SignupResponse(user.getId(), user.getNickname(), user.getEmail());
    }
}