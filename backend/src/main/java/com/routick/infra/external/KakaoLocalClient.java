package com.routick.infra.external.kakao;

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
import java.util.Optional;

// 카카오 로컬 API: 키워드 장소 검색 (지역추천 placeId 매칭, 놀거리 수집 공용)
@Slf4j
@Component
public class KakaoLocalClient {

    private static final String KEYWORD_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json";

    private final RestClient restClient = RestClient.create();

    @Value("${external.kakao.api-key}")
    private String apiKey;

    // 검색 결과 한 건 (placeId 매칭용)
    public record KakaoPlace(
            String placeId,
            String name,
            String address,        // 지번
            String roadAddress,    // 도로명
            Double lat,
            Double lng,
            String category,       // 카카오 카테고리 전체명
            String placeUrl        // 카카오맵 링크
    ) {
    }

    // 키워드 검색 (좌표 기준 반경 내, size개)
    public List<KakaoPlace> search(String keyword, Double lat, Double lng, int radiusM, int size) {
        try {
            String url = UriComponentsBuilder.fromUriString(KEYWORD_SEARCH_URL)
                    .queryParam("query", keyword)
                    .queryParam("y", lat)          // 카카오는 y=위도, x=경도
                    .queryParam("x", lng)
                    .queryParam("radius", radiusM)
                    .queryParam("size", size)
                    .queryParam("sort", "accuracy")
                    .build()
                    .toUriString();

            JsonNode response = restClient.get()
                    .uri(url)
                    .header("Authorization", "KakaoAK " + apiKey)
                    .retrieve()
                    .body(JsonNode.class);

            List<KakaoPlace> places = new ArrayList<>();
            for (JsonNode doc : response.path("documents")) {
                places.add(new KakaoPlace(
                        doc.path("id").asText(),
                        doc.path("place_name").asText(),
                        doc.path("address_name").asText(null),
                        doc.path("road_address_name").asText(null),
                        doc.path("y").asDouble(),
                        doc.path("x").asDouble(),
                        doc.path("category_name").asText(null),
                        doc.path("place_url").asText(null)));
            }
            return places;

        } catch (Exception e) {
            log.error("카카오 로컬 검색 실패: {}", keyword, e);
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }
    }

    // 첫 번째 결과만 (LLM이 추출한 장소명 → placeId 매칭용, 없으면 empty)
    public Optional<KakaoPlace> searchFirst(String keyword, Double lat, Double lng, int radiusM) {
        List<KakaoPlace> results = search(keyword, lat, lng, radiusM, 1);
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }
}