package com.routick.domain.course.controller;

import com.routick.domain.course.dto.CourseGenerateRequest;
import com.routick.domain.course.dto.CourseGenerateResponse;
import com.routick.domain.course.dto.PreferenceCreateRequest;
import com.routick.domain.course.dto.PreferenceCreateResponse;
import com.routick.domain.course.service.CourseService;
import com.routick.domain.course.service.PreferenceService;
import com.routick.global.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/courses")
@RequiredArgsConstructor
public class CourseController {

    private final PreferenceService preferenceService;
    private final CourseService courseService;

    // 선호도 저장
    @PostMapping("/preferences")
    public ApiResponse<PreferenceCreateResponse> createPreference(
            @Valid @RequestBody PreferenceCreateRequest request) {
        PreferenceCreateResponse response = preferenceService.createPreference(request);
        return ApiResponse.success("선호도가 저장되었습니다.", response);
    }

    // 여행 코스 생성 (AI)
    @PostMapping("/generate")
    public ApiResponse<CourseGenerateResponse> generateCourse(
            @Valid @RequestBody CourseGenerateRequest request) {
        CourseGenerateResponse response = courseService.generateCourse(request.preferenceId());
        return ApiResponse.success("코스가 생성되었습니다.", response);
    }
}