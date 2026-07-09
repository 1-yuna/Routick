package com.routick.domain.course.service;

import com.routick.domain.course.dto.CourseGenerateResponse;
import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import com.routick.infra.agent.AgentApiClient;
import com.routick.infra.agent.AgentRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class CourseService {

    // AI 상태값 → 명세서 enum 변환표
    private static final Map<String, String> STATUS_MAP = Map.of(
            "영업 중", "OPEN",
            "브레이크 타임", "BREAK_TIME",
            "휴무", "CLOSED"
    );

    private final PreferenceRepository preferenceRepository;
    private final AgentApiClient agentApiClient;

    // 여행 코스 생성
    @Transactional(readOnly = true)
    public CourseGenerateResponse generateCourse(Long preferenceId) {
        Preference preference = preferenceRepository.findById(preferenceId)
                .orElseThrow(() -> new CustomException(ErrorCode.PREFERENCE_NOT_FOUND));

        if (!preference.getUser().getId().equals(SecurityUtil.getCurrentUserId())) {
            throw new CustomException(ErrorCode.FORBIDDEN);
        }

        CourseGenerateResponse response = agentApiClient.generate(AgentRequest.from(preference));

        response.setPreferenceId(preferenceId);
        convertStatus(response);
        return response;
    }

    // AI의 한국어 영업 상태 → enum 문자열 (OPEN/BREAK_TIME/CLOSED/UNKNOWN)
    private void convertStatus(CourseGenerateResponse response) {
        if (response.getDays() == null) return;
        response.getDays().forEach(day -> {
            if (day.getBlocks() == null) return;
            day.getBlocks().forEach(block -> {
                if ("place".equals(block.getType())) {
                    block.setStatus(STATUS_MAP.getOrDefault(block.getStatus(), "UNKNOWN"));
                }
            });
        });
    }
}