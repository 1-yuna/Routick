// domain/user/controller/ProfileImageController.java
package com.routick.domain.user.controller;

import com.routick.domain.user.entity.ProfileImage;
import com.routick.domain.user.repository.ProfileImageRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/images/profile")
@RequiredArgsConstructor
public class ProfileImageController {

    private final ProfileImageRepository profileImageRepository;

    @GetMapping("/{userId}")
    public ResponseEntity<byte[]> getProfileImage(@PathVariable Long userId) {
        ProfileImage image = profileImageRepository.findById(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(image.getContentType()))
                .body(image.getData());
    }
}