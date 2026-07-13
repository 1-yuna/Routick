package com.routick.domain.auth.service;

import com.routick.domain.auth.dto.TokenPair;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.entity.enums.Provider;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.infra.oauth.OAuthApiClient;
import com.routick.infra.oauth.OAuthUserInfo;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// 소셜 로그인: 사용자 정보 조회 → 로그인 or 자동 가입 → 토큰 발급
@Service
@RequiredArgsConstructor
public class OAuthService {

    private final OAuthApiClient oAuthApiClient;
    private final UserRepository userRepository;
    private final TokenService tokenService;

    @Transactional
    public TokenPair socialLogin(Provider provider, String code) {
        OAuthUserInfo info = oAuthApiClient.fetchUserInfo(provider, code);

        // 이메일 미제공(카카오 선택 동의 거부 등) 시 가입 불가 — 이메일이 계정 식별자라서
        if (info.email() == null) {
            throw new CustomException(ErrorCode.OAUTH_FAILED, "이메일 제공에 동의해주세요.");
        }

        User user = userRepository.findByEmail(info.email())
                .map(existing -> {
                    // 같은 이메일이 다른 수단으로 가입돼 있으면 거절 (이메일당 1수단 정책)
                    if (existing.getProvider() != provider) {
                        throw new CustomException(ErrorCode.EMAIL_DIFFERENT_PROVIDER,
                                "이미 " + existing.getProvider().getLabel() + "로 가입된 이메일입니다.");
                    }
                    return existing;   // 기존 회원 → 로그인
                })
                .orElseGet(() -> signupSocialUser(provider, info));   // 신규 → 자동 가입

        return tokenService.issue(user.getId());
    }

    // 소셜 자동 가입
    private User signupSocialUser(Provider provider, OAuthUserInfo info) {
        return userRepository.save(User.builder()
                .email(info.email())
                .nickname(resolveNickname(info))
                .profileImageUrl(info.profileImageUrl())
                .provider(provider)
                .providerId(info.providerId())
                .build());   // password는 null (소셜 가입)
    }

    // 닉네임: 소셜 닉네임 → 없으면 이메일 앞부분, 10자 제한
    private String resolveNickname(OAuthUserInfo info) {
        String nickname = info.nickname() != null && !info.nickname().isBlank()
                ? info.nickname()
                : info.email().split("@")[0];
        return nickname.length() > 10 ? nickname.substring(0, 10) : nickname;
    }
}