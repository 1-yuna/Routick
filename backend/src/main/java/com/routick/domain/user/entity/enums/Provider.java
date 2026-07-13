package com.routick.domain.user.entity.enums;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

// 가입 방식
@Getter
@RequiredArgsConstructor
public enum Provider {
    EMAIL("이메일"), KAKAO("카카오"), NAVER("네이버"), GOOGLE("구글");

    private final String label;
}