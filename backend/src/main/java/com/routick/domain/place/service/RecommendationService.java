package com.routick.domain.place.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.routick.domain.place.dto.RecommendationResponse;
import com.routick.domain.place.entity.LocalRecommendation;
import com.routick.domain.place.entity.RecommendationItem;
import com.routick.domain.place.repository.LocalRecommendationRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.infra.external.google.GooglePlacesClient;
import com.routick.infra.external.kakao.KakaoLocalClient;
import com.routick.infra.external.naver.NaverBlogClient;
import com.routick.infra.external.openai.OpenAiClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

// 지역추천 TOP5: 30일 캐시 + 갱신 파이프라인 (블로그 → LLM → 카카오 매칭 → 구글 이미지)
@Slf4j
@Service
@RequiredArgsConstructor
public class RecommendationService {

    private static final int CACHE_DAYS = 30;          // 캐시 유효기간
    private static final int BLOG_COUNT = 10;          // 수집할 블로그 수
    private static final int TOP_COUNT = 5;            // 추천 장소 수
    private static final int MATCH_RADIUS_M = 5000;    // 카카오 매칭 반경 (지역 중심 기준 5km)

    private static final String SYSTEM_PROMPT = """
            너는 여행 트렌드 분석가야. 블로그 글들에서 자주 언급되는 인기 장소를 추출해.
            반드시 아래 JSON 형식으로만 응답해:
            {"places": [{"title": "장소명", "reason": "추천 이유 (30자 이내)", "tags": ["태그1", "태그2"]}]}
            규칙:
            - 정확히 %d개 추출, 언급 빈도가 높고 긍정적인 곳 우선
            - title은 검색 가능한 실제 상호명으로 (블로그에 적힌 그대로)
            - tags는 "#감자 요리" 같은 형태 말고 "감자 요리"처럼 2개씩
            - 광고성 글로 보이는 장소는 제외
            """.formatted(TOP_COUNT);

    private final LocalRecommendationRepository recommendationRepository;
    private final NaverBlogClient naverBlogClient;
    private final OpenAiClient openAiClient;
    private final KakaoLocalClient kakaoLocalClient;
    private final GooglePlacesClient googlePlacesClient;
    private final ObjectMapper objectMapper;

    // 지역추천 TOP5 조회 (캐시 우선)
    @Transactional
    public RecommendationResponse getRecommendations(String regionName, Double lat, Double lng) {
        LocalRecommendation cached = recommendationRepository.findByRegionName(regionName).orElse(null);

        // 캐시가 있고 30일 이내면 그대로 응답 (외부 API 호출 없음)
        if (cached != null && cached.getLastUpdatedAt().isAfter(LocalDateTime.now().minusDays(CACHE_DAYS))) {
            return RecommendationResponse.from(cached);
        }

        // 캐시 없음/만료 → 갱신 파이프라인 실행
        LocalRecommendation refreshed = refresh(cached, regionName, lat, lng);
        return RecommendationResponse.from(refreshed);
    }

    // 갱신 파이프라인: 블로그 수집 → LLM 추출 → 카카오 매칭 → 구글 이미지 → 저장
    private LocalRecommendation refresh(LocalRecommendation existing, String regionName, Double lat, Double lng) {
        // ① 블로그 snippet 수집
        String query = regionName + " 맛집 카페 놀거리 추천";
        List<String> snippets = naverBlogClient.searchSnippets(query, BLOG_COUNT);

        // ② LLM으로 장소 추출
        String content = openAiClient.chat(SYSTEM_PROMPT, String.join("\n---\n", snippets));
        List<RecommendationItem> items = parseAndEnrich(content, lat, lng);
        if (items.isEmpty()) {
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }

        // ⑤ 저장 (기존 캐시가 있으면 아이템 교체, 없으면 새로 생성)
        LocalRecommendation recommendation = existing != null ? existing
                : LocalRecommendation.builder()
                .regionName(regionName)
                .searchLat(lat)
                .searchLng(lng)
                .lastUpdatedAt(LocalDateTime.now())
                .build();

        recommendation.replaceItems(items, LocalDateTime.now());
        return recommendationRepository.save(recommendation);
    }

    // LLM 응답 파싱 + ③ 카카오 placeId 매칭 + ④ 구글 이미지
    private List<RecommendationItem> parseAndEnrich(String llmContent, Double lat, Double lng) {
        List<RecommendationItem> items = new ArrayList<>();
        try {
            JsonNode places = objectMapper.readTree(llmContent).path("places");
            int rank = 1;

            for (JsonNode place : places) {
                if (rank > TOP_COUNT) break;
                String title = place.path("title").asText(null);
                if (title == null || title.isBlank()) continue;

                // ③ 카카오 매칭 (실패 시 placeId null — 상세 이동만 불가)
                String placeId = kakaoLocalClient.searchFirst(title, lat, lng, MATCH_RADIUS_M)
                        .map(KakaoLocalClient.KakaoPlace::placeId)
                        .orElse(null);

                // ④ 구글 이미지 (실패 시 null — 플레이스홀더 렌더링)
                String imageUrl = googlePlacesClient.findImageUrl(title).orElse(null);

                List<String> tags = new ArrayList<>();
                place.path("tags").forEach(tag -> tags.add(tag.asText()));

                items.add(RecommendationItem.builder()
                        .title(title)
                        .reason(place.path("reason").asText(null))
                        .tag(tags)
                        .imageUrl(imageUrl)
                        .placeId(placeId)
                        .rank(rank++)
                        .build());
            }
        } catch (Exception e) {
            log.error("LLM 응답 파싱 실패: {}", llmContent, e);
        }
        return items;
    }
}