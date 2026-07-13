package com.routick.domain.course.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "preference_days")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PreferenceDay {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "preference_id", nullable = false)
    private Preference preference;

    @Column(nullable = false)
    private Integer dayNumber;

    @Column(nullable = false)
    private Double startLat;
    @Column(nullable = false)
    private Double startLng;
    private String startName;
    @Column(columnDefinition = "TEXT")
    private String startAddress;
    private String startPlaceId;             // 카카오 장소 ID

    private Double midLat;                   // 놀고 싶은 지역 (선택)
    private Double midLng;
    private String midName;

    @Column(nullable = false)
    private Double endLat;
    @Column(nullable = false)
    private Double endLng;
    private String endName;
    @Column(columnDefinition = "TEXT")
    private String endAddress;
    private String endPlaceId;
}