package com.routick.domain.place.entity;

import com.routick.domain.place.entity.enums.Category;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "place_cache_areas")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PlaceCacheArea {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String regionName;

    @Column(nullable = false)
    private Double searchLat;

    @Column(nullable = false)
    private Double searchLng;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Category category;

    @Column(nullable = false)
    private LocalDateTime lastUpdatedAt;     // 마지막 갱신일 (30일 캐시 판단 기준)

    @Builder.Default
    @OneToMany(mappedBy = "area", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<PlaceCacheItem> items = new ArrayList<>();
}