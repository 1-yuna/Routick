package com.routick.global.exception;

import lombok.Getter;

// 비즈니스 로직에서 던지는 커스텀 예외 (ErrorCode를 담아 GlobalExceptionHandler로 전달)
@Getter
public class CustomException extends RuntimeException {

    private final ErrorCode errorCode;

    // ErrorCode를 받아 예외 생성
    public CustomException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }
}