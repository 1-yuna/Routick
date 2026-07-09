package com.routick.domain.trip.entity;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.user.entity.User;
import com.routick.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "trips")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class Trip extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "preference_id", nullable = false)
    private Preference preference;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String coverImageUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Transport transport;             // 목록 조회용 (preference에서 복사)

    private String region;                   // 목적지 지역명 (routeType=ONLY)
    private String startRegion;              // 시작 지역명 (routeType=ENDPOINT)
    private String endRegion;                // 도착 지역명 (routeType=ENDPOINT)

    @Builder.Default
    @OneToMany(mappedBy = "trip", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TripDay> days = new ArrayList<>();
}