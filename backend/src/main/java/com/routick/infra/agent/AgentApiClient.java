package com.routick.infra.agent;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.routick.domain.course.dto.CourseGenerateResponse;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import java.time.Duration;

@Slf4j
@Component
public class AgentApiClient {

    // AI 응답(snake_case) 전용 매퍼: image_url → imageUrl 자동 매핑
    private final ObjectMapper snakeMapper = new ObjectMapper()
            .setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Value("${agent.base-url}")
    private String baseUrl;

    @Value("${agent.mock:false}")
    private boolean mock;

    // AI 서버에 코스 생성 요청 (타임아웃 60초)
    public CourseGenerateResponse generate(AgentRequest request) {
        if (mock) {
            return loadMockResponse();
        }

        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(3));
        factory.setReadTimeout(Duration.ofSeconds(60));

        try {
            String body = RestClient.builder()
                    .requestFactory(factory)
                    .build()
                    .post()
                    .uri(baseUrl + "/api/generate")
                    .body(request)
                    .retrieve()
                    .body(String.class);

            return snakeMapper.readValue(body, CourseGenerateResponse.class);

        } catch (ResourceAccessException e) {
            // 연결 실패·타임아웃
            log.error("AI 서버 호출 실패", e);
            throw new CustomException(ErrorCode.GENERATION_TIMEOUT);
        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            // AI 서버 에러 응답, 파싱 실패 등
            log.error("AI 코스 생성 실패", e);
            throw new CustomException(ErrorCode.GENERATION_FAILED);
        }
    }

    // mock 모드: 샘플 JSON 반환 (snake_case 파일을 snake 매퍼로 읽음)
    private CourseGenerateResponse loadMockResponse() {
        try {
            return snakeMapper.readValue(
                    new ClassPathResource("mock/generate-response.json").getInputStream(),
                    CourseGenerateResponse.class);
        } catch (Exception e) {
            log.error("mock 응답 로드 실패", e);
            throw new CustomException(ErrorCode.GENERATION_FAILED);
        }
    }
}