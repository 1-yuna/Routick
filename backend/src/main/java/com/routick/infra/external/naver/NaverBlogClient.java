package com.routick.infra.external.naver;

import com.fasterxml.jackson.databind.JsonNode;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.ArrayList;
import java.util.List;

// 네이버 블로그 검색: 지역 트렌드 장소 추출용 snippet 수집
@Slf4j
@Component
public class NaverBlogClient {

    private static final String BLOG_SEARCH_URL = "https://openapi.naver.com/v1/search/blog.json";

    private final RestClient restClient = RestClient.create();

    @Value("${external.naver.client-id}")
    private String clientId;

    @Value("${external.naver.client-secret}")
    private String clientSecret;

    // 블로그 검색 → "제목 + 본문 snippet" 목록 반환
    public List<String> searchSnippets(String query, int display) {
        try {
            String url = UriComponentsBuilder.fromUriString(BLOG_SEARCH_URL)
                    .queryParam("query", query)
                    .queryParam("display", display)
                    .queryParam("sort", "date")          // 최신순 (트렌드 반영)
                    .build()
                    .toUriString();

            JsonNode response = restClient.get()
                    .uri(url)
                    .header("X-Naver-Client-Id", clientId)
                    .header("X-Naver-Client-Secret", clientSecret)
                    .retrieve()
                    .body(JsonNode.class);

            List<String> snippets = new ArrayList<>();
            for (JsonNode item : response.path("items")) {
                snippets.add(stripHtml(item.path("title").asText("")) + " - "
                        + stripHtml(item.path("description").asText("")));
            }
            return snippets;

        } catch (Exception e) {
            log.error("네이버 블로그 검색 실패: {}", query, e);
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }
    }

    // 네이버 응답의 <b> 태그 등 제거
    private String stripHtml(String text) {
        return text.replaceAll("<[^>]*>", "").replace("&quot;", "\"").replace("&amp;", "&");
    }
}