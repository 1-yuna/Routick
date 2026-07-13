// domain/user/entity/ProfileImage.java
package com.routick.domain.user.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "profile_images")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class ProfileImage {

    @Id
    private Long userId;   // User와 1:1, PK 공유 (FK 제약은 안 걸었음 - 임시 방식이라 단순하게)

    @Lob
    @Column(nullable = false)
    private byte[] data;

    @Column(nullable = false)
    private String contentType;

    public static ProfileImage of(Long userId, byte[] data, String contentType) {
        return new ProfileImage(userId, data, contentType);
    }

    public void update(byte[] data, String contentType) {
        this.data = data;
        this.contentType = contentType;
    }
}