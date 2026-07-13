package com.routick.infra.external.openai;

import com.fasterxml.jackson.databind.JsonNode;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

// OpenAI GPT-4o-mini 호출 (JSON 형식 응답 강제)
@Slf4j
@Component
public class OpenAiClient {

    private static final String CHAT_URL = "https://api.openai.com/v1/chat/completions";
    private static final String MODEL = "gpt-4o-mini";

    private final RestClient restClient = RestClient.create();

    @Value("${external.openai.api-key}")
    private String apiKey;

    // system/user 프롬프트로 채팅 호출 → 응답 content(JSON 문자열) 반환
    public String chat(String systemPrompt, String userPrompt) {
        try {
            Map<String, Object> body = Map.of(
                    "model", MODEL,
                    "messages", List.of(
                            Map.of("role", "system", "content", systemPrompt),
                            Map.of("role", "user", "content", userPrompt)),
                    "response_format", Map.of("type", "json_object"),   // JSON만 응답하게 강제
                    "temperature", 0.3
            );

            JsonNode response = restClient.post()
                    .uri(CHAT_URL)
                    .header("Authorization", "Bearer " + apiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(JsonNode.class);

            return response.path("choices").get(0).path("message").path("content").asText();

        } catch (Exception e) {
            log.error("OpenAI 호출 실패", e);
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }
    }
}