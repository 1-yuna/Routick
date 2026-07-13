// domain/user/repository/ProfileImageRepository.java
package com.routick.domain.user.repository;

import com.routick.domain.user.entity.ProfileImage;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileImageRepository extends JpaRepository<ProfileImage, Long> {
}