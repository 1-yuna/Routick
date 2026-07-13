package com.routick.domain.place.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.routick.domain.place.dto.PlaceListResponse;
import com.routick.domain.place.entity.PlaceCacheArea;
import com.routick.domain.place.entity.PlaceCacheItem;
import com.routick.domain.place.entity.enums.Category;
import com.routick.domain.place.repository.PlaceCacheAreaRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.infra.external.google.GooglePlacesClient;
import com.routick.infra.external.kakao.KakaoLocalClient;
import com.routick.infra.external.kakao.KakaoLocalClient.KakaoPlace;
import com.routick.infra.external.naver.NaverBlogClient;
import com.routick.infra.external.openai.OpenAiClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

// 놀거리 카테고리별 조회: 30일 캐시 + 갱신 파이프라인
// - HOTPLACE: 블로그에서 발굴 (트렌드 스팟) → 카카오 매칭
// - FOOD_CAFE/CULTURE_NATURE: 카카오에서 수집 → 블로그 언급 기반 인기순 선별
@Slf4j
@Service
@RequiredArgsConstructor
public class PlaceListService {

    private static final int CACHE_DAYS = 30;
    private static final int ITEM_COUNT = 10;          // 카테고리당 노출 개수
    private static final int CANDIDATE_SIZE = 15;      // 카카오 수집 후보 수 (코드당)
    private static final int SEARCH_RADIUS_M = 2000;   // 수집 반경
    private static final int BLOG_COUNT = 10;

    // 후보 목록에서 인기순 선별 + 설명 생성 (FOOD_CAFE/CULTURE_NATURE)
    private static final String SELECT_PROMPT = """
            너는 지역 큐레이터야. 장소 후보 목록과 블로그 글들이 주어진다.
            블로그에서 언급이 많고 평이 좋은 순서(인기순)로 %d개를 골라.
            반드시 아래 JSON 형식으로만 응답해:
            {"places": [{"name": "후보 목록에 있는 이름 그대로", "short_description": "카드용 1줄 소개", "description": "상세용 3줄 내외 소개"}]}
            규칙:
            - name은 후보 목록의 이름을 한 글자도 바꾸지 말 것
            - 블로그에 안 나오는 후보는 카테고리와 이름으로 추론해 뒤 순위로
            - 배열 순서가 곧 인기 순위
            """.formatted(ITEM_COUNT);

    // 블로그에서 핫플 발굴 (HOTPLACE)
    private static final String HOTPLACE_PROMPT = """
            너는 지역 큐레이터야. 블로그 글들에서 요즘 뜨는 "노는 곳"을 추출해.
            노는 곳이란: 감성 카페, 팝업스토어, 문화공간, 체험·액티비티, 포토스팟 같은 공간.
            (유명 먹거리·특산물 같은 "명물"은 제외 — 그건 다른 섹션에서 다룸)
            반드시 아래 JSON 형식으로만 응답해:
            {"places": [{"name": "검색 가능한 실제 상호명", "short_description": "카드용 1줄 소개", "description": "상세용 3줄 내외 소개"}]}
            규칙:
            - 언급 빈도·화제성 순으로 %d개 (여유분 포함), 배열 순서가 곧 인기 순위
            - 광고성 글로 보이는 장소는 제외
            """.formatted(ITEM_COUNT + 10);

    private final PlaceCacheAreaRepository areaRepository;
    private final KakaoLocalClient kakaoLocalClient;
    private final NaverBlogClient naverBlogClient;
    private final OpenAiClient openAiClient;
    private final GooglePlacesClient googlePlacesClient;
    private final ObjectMapper objectMapper;

    // 놀거리 조회 (캐시 우선)
    @Transactional
    public PlaceListResponse getPlaces(String categoryValue, String regionName, Double lat, Double lng) {
        Category category = parseCategory(categoryValue);

        PlaceCacheArea cached = areaRepository.findByRegionNameAndCategory(regionName, category).orElse(null);
        if (cached != null && cached.getLastUpdatedAt().isAfter(LocalDateTime.now().minusDays(CACHE_DAYS))) {
            return PlaceListResponse.from(cached);
        }

        PlaceCacheArea refreshed = refresh(cached, category, regionName, lat, lng);
        return PlaceListResponse.from(refreshed);
    }

    // 갱신 파이프라인
    private PlaceCacheArea refresh(PlaceCacheArea existing, Category category,
                                   String regionName, Double lat, Double lng) {
        List<PlaceCacheItem> items = switch (category) {
            case HOTPLACE -> collectHotplaces(regionName, lat, lng);
            case FOOD_CAFE -> collectByKakao(category, regionName, lat, lng,
                    List.of("FD6", "CE7"), regionName + " 맛집 카페 추천");
            case CULTURE_NATURE -> collectByKakao(category, regionName, lat, lng,
                    List.of("AT4", "CT1"), regionName + " 가볼만한 곳 명소 추천");
        };

        if (items.isEmpty()) {
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }

        PlaceCacheArea area = existing != null ? existing
                : PlaceCacheArea.builder()
                .regionName(regionName)
                .searchLat(lat)
                .searchLng(lng)
                .category(category)
                .lastUpdatedAt(LocalDateTime.now())
                .build();

        area.replaceItems(items, LocalDateTime.now());
        return areaRepository.save(area);
    }

    // FOOD_CAFE/CULTURE_NATURE: 카카오 수집 → 블로그+LLM 인기순 선별
    private List<PlaceCacheItem> collectByKakao(Category category, String regionName,
                                                Double lat, Double lng,
                                                List<String> categoryCodes, String blogQuery) {
        // ① 카카오 후보 수집 (코드별 15개씩, placeId 기준 중복 제거)
        Map<String, KakaoPlace> candidates = categoryCodes.stream()
                .flatMap(code -> kakaoLocalClient.searchByCategory(code, lat, lng, SEARCH_RADIUS_M, CANDIDATE_SIZE).stream())
                .collect(Collectors.toMap(KakaoPlace::placeId, Function.identity(), (a, b) -> a));

        // ② 블로그 snippet 수집
        List<String> snippets = naverBlogClient.searchSnippets(blogQuery, BLOG_COUNT);

        // ③ LLM: 인기순 선별 + 설명 생성
        String candidateList = candidates.values().stream()
                .map(p -> "- " + p.name() + " (" + p.category() + ")")
                .collect(Collectors.joining("\n"));
        String userPrompt = "[장소 후보]\n" + candidateList + "\n\n[블로그 글]\n" + String.join("\n---\n", snippets);
        String content = openAiClient.chat(SELECT_PROMPT, userPrompt);

        // ④ LLM 결과를 후보와 매칭 + 구글 이미지
        Map<String, KakaoPlace> byName = candidates.values().stream()
                .collect(Collectors.toMap(KakaoPlace::name, Function.identity(), (a, b) -> a));

        List<PlaceCacheItem> items = new ArrayList<>();
        int rank = 1;
        for (JsonNode node : parsePlaces(content)) {
            if (rank > ITEM_COUNT) break;
            KakaoPlace matched = byName.get(node.path("name").asText());
            if (matched == null) continue;   // LLM이 이름을 바꿨으면 스킵

            items.add(buildItem(matched, node, rank++, regionName));
        }
        return items;
    }

    // HOTPLACE: 블로그 발굴 → 카카오 매칭
    private List<PlaceCacheItem> collectHotplaces(String regionName, Double lat, Double lng) {
        // ① 블로그 수집 → ② LLM 발굴
        List<String> snippets = naverBlogClient.searchSnippets(regionName + " 핫플 놀거리 추천", BLOG_COUNT);
        String content = openAiClient.chat(HOTPLACE_PROMPT, String.join("\n---\n", snippets));

        // ③ 카카오 매칭 (실패한 장소는 건너뛰고 다음 순위로 채움)
        // 1차: 이름 그대로 (반경 10km) → 실패 시 2차: "지역명 + 이름"으로 재시도 (반경 20km)
        List<PlaceCacheItem> items = new ArrayList<>();
        int rank = 1;
        for (JsonNode node : parsePlaces(content)) {
            if (rank > ITEM_COUNT) break;
            String name = node.path("name").asText();

            KakaoPlace matched = kakaoLocalClient.searchFirst(name, lat, lng, 10_000)
                    .or(() -> kakaoLocalClient.searchFirst(regionName + " " + name, lat, lng, 20_000))
                    .orElse(null);
            if (matched == null) continue;   // 두 번 다 실패 → 제외

            items.add(buildItem(matched, node, rank++, regionName));
        }
        return items;
    }

    // 카카오 장소 + LLM 설명 + 구글 이미지 → PlaceCacheItem
    private PlaceCacheItem buildItem(KakaoPlace place, JsonNode node, int rank, String regionName) {
        String imageUrl = googlePlacesClient.findImageUrl(regionName + " " + place.name()).orElse(null);
        return PlaceCacheItem.builder()
                .placeId(place.placeId())
                .name(place.name())
                .address(place.roadAddress() != null && !place.roadAddress().isBlank()
                        ? place.roadAddress() : place.address())
                .lat(place.lat())
                .lng(place.lng())
                .imageUrl(imageUrl)
                .description(node.path("short_description").asText(null))     // 1줄
                .longDescription(node.path("description").asText(null))       // 3줄
                .rank(rank)
                .build();
    }

    private JsonNode parsePlaces(String llmContent) {
        try {
            return objectMapper.readTree(llmContent).path("places");
        } catch (Exception e) {
            log.error("LLM 응답 파싱 실패: {}", llmContent, e);
            throw new CustomException(ErrorCode.EXTERNAL_API_ERROR);
        }
    }

    private Category parseCategory(String value) {
        try {
            return Category.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new CustomException(ErrorCode.INVALID_CATEGORY);
        }
    }
}