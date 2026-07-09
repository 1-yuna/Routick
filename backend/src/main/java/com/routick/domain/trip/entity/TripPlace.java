package com.routick.domain.trip.entity;

import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.trip.entity.enums.BlockType;
import com.routick.domain.trip.entity.enums.Bucket;
import com.routick.domain.trip.entity.enums.PlaceStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalTime;

@Entity
@Table(name = "trip_places")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class TripPlace {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "trip_day_id", nullable = false)
    private TripDay tripDay;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private BlockType type;                  // START/PLACE/WALK/PARKING/END

    @Column(nullable = false)
    private Integer blockOrder;              // 타임라인 내 전체 순서

    private Integer placeOrder;              // 장소 방문 순서 (PLACE만, 지도 마커 번호)

    private String placeId;                  // 카카오 장소 ID (START/PLACE/PARKING/END)
    private String name;
    @Column(columnDefinition = "TEXT")
    private String address;
    private Double lat;
    private Double lng;

    @Enumerated(EnumType.STRING)
    private Bucket bucket;                   // PLACE만

    @Column(columnDefinition = "TEXT")
    private String imageUrl;                 // PLACE만

    @Column(columnDefinition = "TEXT")
    private String description;              // PLACE만

    @Enumerated(EnumType.STRING)
    private PlaceStatus status;              // PLACE만

    private Integer stayMinutes;             // PLACE만
    private Integer minutes;                 // WALK만 (이동 시간)

    @Enumerated(EnumType.STRING)
    private Transport transportToNext;       // 다음 블록까지 이동 수단

    private Integer travelMinutesToNext;     // 다음 블록까지 이동 시간

    private LocalTime arriveTime;
    private LocalTime leaveTime;
}