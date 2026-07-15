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
import java.util.Optional;

// 지역추천 TOP5: 30일 캐시 + 갱신 파이프라인 (블로그 → LLM → 카카오 매칭 → 구글 이미지)
@Slf4j
@Service
@RequiredArgsConstructor
public class RecommendationService {

    private static final int CACHE_DAYS = 30;          // 캐시 유효기간
    private static final int BLOG_COUNT = 10;          // 수집할 블로그 수
    private static final int TOP_COUNT = 5;            // 추천 장소 수
    private static final int MATCH_RADIUS_M = 5000;    // 카카오 매칭 반경 (지역 중심 기준 5km)
    private static final int MIN_COUNT = 2;   // 최소 확보 개수

    private static final String SYSTEM_PROMPT = """
        너는 여행 트렌드 분석가야. 블로그 글들에서 이 지역을 대표하는 명물을 추출해.
        명물이란: 그 지역 하면 떠오르는 특정 가게·시장·브랜드의 대표 메뉴/상품이야.
        예: "대림창고", "성수족발", "구제시장 꽈배기" (O) / "성수동 카페", "성수동 맛집", "성수동 전통시장" (X, 카테고리명이라 안 됨)
        반드시 아래 JSON 형식으로만 응답해:
        {"places": [{"title": "장소명", "reason": "추천 이유 (30자 이내)", "tags": ["태그1", "태그2"]}]}
        규칙:
        - 최소 %d개, 최대 %d개. 구체적인 상호명이 확인되는 곳만 골라 (억지로 개수를 채우지 말되, 최소 개수는 꼭 채울 것)
        - title은 검색 가능한 실제 상호명으로 (지역명+업종만 있는 뭉뚱그린 이름 금지)
        - 언급 빈도가 높고 긍정적인 곳, 지역 대표성이 있는 곳 우선
        - 광고성 글로 보이는 장소는 제외
        """.formatted(MIN_COUNT, TOP_COUNT);

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
        // ① 블로그 snippet 수집 — 지역 "명물" 발굴용
        String query = regionName + "top5";
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

                // ③ 카카오 매칭 (실패 시 placeId/lat/lng 모두 null — 상세 이동·지도 표시만 불가)
                Optional<KakaoLocalClient.KakaoPlace> matched =
                        kakaoLocalClient.searchFirst(title, lat, lng, MATCH_RADIUS_M);

// ④ 구글 이미지 (실패 시 null — 플레이스홀더 렌더링)
                String imageUrl = googlePlacesClient.findImageUrl(title).orElse(null);

                List<String> tags = new ArrayList<>();
                place.path("tags").forEach(tag -> tags.add(tag.asText()));

                items.add(RecommendationItem.builder()
                        .title(title)
                        .reason(place.path("reason").asText(null))
                        .tag(tags)
                        .imageUrl(imageUrl)
                        .placeId(matched.map(KakaoLocalClient.KakaoPlace::placeId).orElse(null))
                        .lat(matched.map(KakaoLocalClient.KakaoPlace::lat).orElse(null))
                        .lng(matched.map(KakaoLocalClient.KakaoPlace::lng).orElse(null))
                        .rank(rank++)
                        .build());
            }
        } catch (Exception e) {
            log.error("LLM 응답 파싱 실패: {}", llmContent, e);
        }
        return items;
    }
}