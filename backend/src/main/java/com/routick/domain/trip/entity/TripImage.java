package com.routick.domain.trip.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "trip_images")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class TripImage {

    @Id
    private Long tripPlaceId;   // PK이자 trip_place.id 공유 (식별관계)

    @Lob
    @Column(nullable = false)
    private byte[] data;

    @Column(nullable = false)
    private String contentType;

    public static TripImage of(Long tripPlaceId, byte[] data, String contentType) {
        return new TripImage(tripPlaceId, data, contentType);
    }
}