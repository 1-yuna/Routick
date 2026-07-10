package com.routick.infra.external.google;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Optional;

// 구글 Places API: 장소 대표 이미지 조회 (Basic SKU)
// 이미지 실패는 서비스 품질 저하일 뿐이라 예외 대신 empty 반환 (다른 클라이언트와 다른 점)
@Slf4j
@Component
public class GooglePlacesClient {

    private static final String FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json";
    private static final String DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json";
    private static final String PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo";

    private final RestClient restClient = RestClient.create();

    // photo 엔드포인트의 302 리다이렉트를 직접 잡기 위한 클라이언트 (아래 주석 참고)
    private final HttpClient httpClient = HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NEVER)
            .build();

    @Value("${external.google.places-api-key}")
    private String apiKey;

    // 장소명 → 대표 이미지 URL (실패 시 empty)
    public Optional<String> findImageUrl(String placeName) {
        try {
            // 1. 장소명 → 구글 place_id
            String findUrl = UriComponentsBuilder.fromUriString(FIND_PLACE_URL)
                    .queryParam("input", placeName)
                    .queryParam("inputtype", "textquery")
                    .queryParam("fields", "place_id")
                    .queryParam("key", apiKey)
                    .build().toUriString();

            JsonNode findResponse = restClient.get().uri(findUrl).retrieve().body(JsonNode.class);
            JsonNode candidates = findResponse.path("candidates");
            if (candidates.isEmpty()) return Optional.empty();
            String placeId = candidates.get(0).path("place_id").asText();

            // 2. place_id → photo_reference
            String detailsUrl = UriComponentsBuilder.fromUriString(DETAILS_URL)
                    .queryParam("place_id", placeId)
                    .queryParam("fields", "photos")
                    .queryParam("key", apiKey)
                    .build().toUriString();

            JsonNode detailsResponse = restClient.get().uri(detailsUrl).retrieve().body(JsonNode.class);
            JsonNode photos = detailsResponse.path("result").path("photos");
            if (photos.isEmpty()) return Optional.empty();
            String photoReference = photos.get(0).path("photo_reference").asText();

            // 3. photo API는 실제 이미지 주소로 302 리다이렉트를 줌.
            //    리다이렉트된 최종 URL(googleusercontent)을 저장해야
            //    API 키가 박힌 URL이 프론트/DB에 노출되지 않음
            String photoUrl = UriComponentsBuilder.fromUriString(PHOTO_URL)
                    .queryParam("maxwidth", 400)
                    .queryParam("photo_reference", photoReference)
                    .queryParam("key", apiKey)
                    .build().toUriString();

            HttpResponse<Void> response = httpClient.send(
                    HttpRequest.newBuilder(URI.create(photoUrl)).GET().build(),
                    HttpResponse.BodyHandlers.discarding());

            return response.headers().firstValue("location");   // 키 없는 실제 이미지 URL

        } catch (Exception e) {
            log.warn("구글 이미지 조회 실패: {}", placeName);
            return Optional.empty();
        }
    }
}