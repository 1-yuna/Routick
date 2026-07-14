package com.routick.domain.place.dto;

import com.routick.domain.place.entity.LocalRecommendation;
import com.routick.domain.place.entity.RecommendationItem;

import java.util.List;

// 지역추천 TOP5 응답
public record RecommendationResponse(String regionName, List<Item> items) {

    public record Item(
            Integer rank,
            String title,
            String imageUrl,
            String reason,
            List<String> tags,
            String placeId,     // 카카오 매칭 실패 시 null → 프론트에서 클릭 불가 처리
             Double lat,           // 매칭 실패 시 null
            Double lng
    ) {
        public static Item from(RecommendationItem item) {
            return new Item(item.getRank(), item.getTitle(), item.getImageUrl(),
                    item.getReason(), item.getTag(), item.getPlaceId(), item.getLat(), item.getLng());
        }
    }

    public static RecommendationResponse from(LocalRecommendation recommendation) {
        List<Item> items = recommendation.getItems().stream()
                .sorted((a, b) -> a.getRank().compareTo(b.getRank()))
                .map(Item::from)
                .toList();
        return new RecommendationResponse(recommendation.getRegionName(), items);
    }
}