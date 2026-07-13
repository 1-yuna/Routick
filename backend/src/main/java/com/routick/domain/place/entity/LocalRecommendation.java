package com.routick.domain.place.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "local_recommendations")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class LocalRecommendation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String regionName;               // 검색 지역명

    @Column(nullable = false)
    private Double searchLat;                // 검색 기준 좌표

    @Column(nullable = false)
    private Double searchLng;

    @Column(nullable = false)
    private LocalDateTime lastUpdatedAt;     // 마지막 갱신일 (30일 캐시 판단 기준)

    @Builder.Default
    @OneToMany(mappedBy = "recommendation", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<RecommendationItem> items = new ArrayList<>();

    // 캐시 갱신: 기존 아이템 전체 교체 + 갱신 시각 기록
    public void replaceItems(List<RecommendationItem> newItems, LocalDateTime updatedAt) {
        this.items.clear();
        newItems.forEach(item -> {
            item.assignRecommendation(this);
            this.items.add(item);
        });
        this.lastUpdatedAt = updatedAt;
    }
}