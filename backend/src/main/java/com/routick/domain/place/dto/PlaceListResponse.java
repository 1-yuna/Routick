package com.routick.domain.place.dto;

import com.routick.domain.place.entity.PlaceCacheArea;
import com.routick.domain.place.entity.PlaceCacheItem;

import java.util.Comparator;
import java.util.List;

// 놀거리 카테고리별 조회 응답
public record PlaceListResponse(String category, String regionName, List<Item> items) {

    public record Item(
            String placeId,
            Integer rank,
            String name,
            String longDescription,      // 상세용 긴 설명
            String address,
            String imageUrl
    ) {
        public static Item from(PlaceCacheItem item) {
            return new Item(item.getPlaceId(), item.getRank(), item.getName(),
                    item.getLongDescription(), item.getAddress(), item.getImageUrl());
        }
    }

    public static PlaceListResponse from(PlaceCacheArea area) {
        List<Item> items = area.getItems().stream()
                .sorted(Comparator.comparing(PlaceCacheItem::getRank))
                .map(Item::from)
                .toList();
        return new PlaceListResponse(area.getCategory().name(), area.getRegionName(), items);
    }
}