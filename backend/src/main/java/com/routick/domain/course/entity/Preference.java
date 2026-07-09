package com.routick.domain.course.entity;

import com.routick.domain.course.entity.enums.Companion;
import com.routick.domain.course.entity.enums.RouteType;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.user.entity.User;
import com.routick.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "preferences")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class Preference extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private Integer travelDays;              // 1=당일 ~ 4=3박4일

    @Column(nullable = false)
    private LocalDate travelDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Transport transport;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RouteType routeType;

    private String destination;              // 목적지 지역명 (routeType=ONLY)
    private Double lat;                      // 목적지 위도 (routeType=ONLY)
    private Double lng;                      // 목적지 경도 (routeType=ONLY)

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Companion companion;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> moods;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> activities;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<String> avoidActivities;
}