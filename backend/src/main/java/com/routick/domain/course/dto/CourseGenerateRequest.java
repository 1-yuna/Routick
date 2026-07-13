package com.routick.domain.course.dto;

import jakarta.validation.constraints.NotNull;

// 코스 생성 요청
public record CourseGenerateRequest(@NotNull Long preferenceId) {
}