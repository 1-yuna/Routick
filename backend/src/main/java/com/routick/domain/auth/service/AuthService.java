package com.routick.domain.auth.service;

import com.routick.domain.user.entity.enums.Provider;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.time.Duration;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private static final Duration CODE_TTL = Duration.ofMinutes(2);   // 인증번호 유효시간
    private static final String CODE_KEY_PREFIX = "email:";

    private static final Map<Provider, String> PROVIDER_LABELS = Map.of(
            Provider.KAKAO, "카카오", Provider.NAVER, "네이버", Provider.GOOGLE, "구글");

    private final UserRepository userRepository;
    private final StringRedisTemplate redisTemplate;
    private final JavaMailSender mailSender;

    // 이메일 인증번호 발송
    public void sendEmailCode(String email) {
        // 가입 여부 검사 (수단별 에러 분기)
        userRepository.findByEmail(email).ifPresent(user -> {
            if (user.getProvider() == Provider.EMAIL) {
                throw new CustomException(ErrorCode.EMAIL_ALREADY_EXISTS);
            }
            throw new CustomException(ErrorCode.EMAIL_DIFFERENT_PROVIDER,
                    "이미 " + PROVIDER_LABELS.get(user.getProvider()) + "로 가입된 이메일입니다.");
        });

        // 6자리 인증번호 생성
        String code = String.format("%06d", new SecureRandom().nextInt(1_000_000));

        // 메일 발송
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(email);
            message.setSubject("[Routick] 이메일 인증번호");
            message.setText("인증번호: " + code + "\n\n2분 안에 입력해주세요.");
            mailSender.send(message);
        } catch (Exception e) {
            throw new CustomException(ErrorCode.EMAIL_SEND_FAILED);
        }

        // 발송 성공 시에만 Redis 저장 (TTL 2분)
        redisTemplate.opsForValue().set(CODE_KEY_PREFIX + email, code, CODE_TTL);
    }
}