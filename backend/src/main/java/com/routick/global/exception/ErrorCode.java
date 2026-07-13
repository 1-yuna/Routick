package com.routick.global.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    // 공통
    INVALID_INPUT(HttpStatus.BAD_REQUEST, "입력값이 올바르지 않습니다."),
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다."),
    TOKEN_EXPIRED(HttpStatus.UNAUTHORIZED, "토큰이 만료되었습니다."),
    INVALID_TOKEN(HttpStatus.UNAUTHORIZED, "유효하지 않은 토큰입니다."),
    FORBIDDEN(HttpStatus.FORBIDDEN, "접근 권한이 없습니다."),
    INTERNAL_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "일시적인 오류가 발생했습니다."),

    // Auth
    EMAIL_ALREADY_EXISTS(HttpStatus.CONFLICT, "이미 가입된 계정입니다."),
    EMAIL_DIFFERENT_PROVIDER(HttpStatus.CONFLICT, "다른 방식으로 가입된 이메일입니다."),
    EMAIL_SEND_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "인증번호 발송에 실패했습니다."),
    CODE_MISMATCH(HttpStatus.BAD_REQUEST, "인증번호가 일치하지 않습니다."),
    CODE_EXPIRED(HttpStatus.BAD_REQUEST, "인증번호가 만료되었습니다. 다시 요청해주세요."),
    CODE_ATTEMPT_EXCEEDED(HttpStatus.TOO_MANY_REQUESTS, "인증 시도 횟수를 초과했습니다. 다시 요청해주세요."),
    EMAIL_NOT_VERIFIED(HttpStatus.BAD_REQUEST, "이메일 인증을 완료해주세요."),
    INVALID_PASSWORD_FORMAT(HttpStatus.BAD_REQUEST, "비밀번호는 8자 이상, 영문/숫자를 포함해주세요."),
    USER_NOT_FOUND(HttpStatus.NOT_FOUND, "가입이 안 된 계정입니다."),
    PASSWORD_MISMATCH(HttpStatus.UNAUTHORIZED, "비밀번호가 일치하지 않습니다."),
    INVALID_REFRESH_TOKEN(HttpStatus.UNAUTHORIZED, "다시 로그인해주세요."),
    OAUTH_FAILED(HttpStatus.BAD_REQUEST, "소셜 로그인에 실패했습니다."),

    // User
    INVALID_NICKNAME(HttpStatus.BAD_REQUEST, "닉네임은 2~10자로 입력해주세요."),
    IMAGE_UPLOAD_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "이미지 업로드에 실패했습니다."),

    // Place
    PLACE_NOT_FOUND(HttpStatus.NOT_FOUND, "장소를 찾을 수 없습니다."),
    INVALID_CATEGORY(HttpStatus.BAD_REQUEST, "존재하지 않는 카테고리입니다."),
    EXTERNAL_API_ERROR(HttpStatus.BAD_GATEWAY, "외부 API 호출에 실패했습니다."),

    // 여행 생성 (course)
    DISTANCE_EXCEEDED(HttpStatus.BAD_REQUEST, "이동수단 기준 거리를 초과했습니다."),
    PREFERENCE_NOT_FOUND(HttpStatus.NOT_FOUND, "선호도 정보를 찾을 수 없습니다."),
    GENERATION_FAILED(HttpStatus.BAD_GATEWAY, "일정 생성에 실패했어요."),
    GENERATION_TIMEOUT(HttpStatus.GATEWAY_TIMEOUT, "일정 생성에 실패했어요."),

    // 내 여행 (trip)
    TRIP_NOT_FOUND(HttpStatus.NOT_FOUND, "여행을 찾을 수 없습니다.");

    private final HttpStatus status;
    private final String message;
}