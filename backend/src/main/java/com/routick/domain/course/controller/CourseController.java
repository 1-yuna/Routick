package com.routick.domain.course.controller;

import com.routick.domain.course.dto.CourseGenerateRequest;
import com.routick.domain.course.dto.CourseGenerateResponse;
import com.routick.domain.course.dto.PreferenceCreateRequest;
import com.routick.domain.course.dto.PreferenceCreateResponse;
import com.routick.domain.course.service.CourseService;
import com.routick.domain.course.service.PreferenceService;
import com.routick.global.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/courses")
@RequiredArgsConstructor
@Tag(name = "Course", description = "여행 코스 생성")
public class CourseController {

    private final PreferenceService preferenceService;
    private final CourseService courseService;

    // 선호도 저장
    @Operation(summary = "선호도 저장", description = "코스 생성 조건(기간·이동수단·동선·취향)을 저장하고 preferenceId를 반환한다")
    @PostMapping("/preferences")
    public ApiResponse<PreferenceCreateResponse> createPreference(
            @Valid @RequestBody PreferenceCreateRequest request) {
        PreferenceCreateResponse response = preferenceService.createPreference(request);
        return ApiResponse.success("선호도가 저장되었습니다.", response);
    }

    // 여행 코스 생성 (AI)
    @Operation(summary = "여행 코스 생성", description = "AI 서버를 호출해 일정표를 생성한다 (저장 안 됨, 재추천 시 동일 preferenceId로 재호출, 타임아웃 60초)")
    @PostMapping("/generate")
    public ApiResponse<CourseGenerateResponse> generateCourse(
            @Valid @RequestBody CourseGenerateRequest request) {
        CourseGenerateResponse response = courseService.generateCourse(request.preferenceId());
        return ApiResponse.success("코스가 생성되었습니다.", response);
    }
}