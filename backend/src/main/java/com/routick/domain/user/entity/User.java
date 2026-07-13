package com.routick.domain.user.entity;

import com.routick.domain.user.entity.enums.Provider;
import com.routick.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class User extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 10)
    private String nickname;

    @Column(nullable = false, unique = true)
    private String email;

    private String password;                 // 소셜 가입이면 null

    @Column(columnDefinition = "TEXT")
    private String profileImageUrl;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Provider provider;               // 가입 방식

    private String providerId;               // 소셜 고유 ID (이메일 가입이면 null)

    private String lastLocationRegionName;   // 마지막 선택 지역명
    private Double lastLocationLat;
    private Double lastLocationLng;

    // 프로필 수정: null이 아닌 값만 반영
    public void updateProfile(String nickname, String profileImageUrl) {
        if (nickname != null) this.nickname = nickname;
        if (profileImageUrl != null) this.profileImageUrl = profileImageUrl;
    }

    // 마지막 선택 위치 저장
    public void updateLastLocation(String regionName, Double lat, Double lng) {
        this.lastLocationRegionName = regionName;
        this.lastLocationLat = lat;
        this.lastLocationLng = lng;
    }
}