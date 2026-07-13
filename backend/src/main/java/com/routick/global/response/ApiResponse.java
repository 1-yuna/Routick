package com.routick.global.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class ApiResponse<T> {

    private final boolean success;
    private final String message;

    @JsonInclude(JsonInclude.Include.NON_NULL)
    private final String code;   // 에러일 때만 포함

    private final T data;

    // 성공 응답 (메시지 + 데이터 직접 지정)
    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>(true, message, null, data);
    }

    // 성공 응답 (기본 메시지 + 데이터)
    public static <T> ApiResponse<T> success(T data) {
        return success("요청이 성공했습니다.", data);
    }

    // 성공 응답 (메시지만, 데이터 없음)
    public static ApiResponse<Void> success(String message) {
        return success(message, null);
    }

    // 에러 응답 (메시지 + 에러 코드)
    public static ApiResponse<Void> error(String message, String code) {
        return new ApiResponse<>(false, message, code, null);
    }
}