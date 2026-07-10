package com.routick.domain.place.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "place_cache_items")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PlaceCacheItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "area_id", nullable = false)
    private PlaceCacheArea area;

    @Column(nullable = false)
    private String placeId;                  // 카카오 장소 ID

    @Column(nullable = false)
    private String name;

    private String address;

    @Column(nullable = false)
    private Double lat;

    @Column(nullable = false)
    private Double lng;

    @Column(columnDefinition = "TEXT")
    private String imageUrl;

    private String description;         // 카드용 1줄 설명 (그대로)

    @Column(columnDefinition = "TEXT")
    private String longDescription;          // 상세용 3줄 설명 ← description에서 변경              // 상세페이지용 3줄 설명

    @Column(nullable = false)
    private Integer rank;                    // 추천 순위 (1~10)

    // PlaceCacheItem.java
    // 부모 연결 (캐시 갱신 시 사용)
    public void assignArea(PlaceCacheArea area) {
        this.area = area;
    }
}