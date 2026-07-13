package com.routick.domain.user.service;

import com.routick.domain.auth.service.TokenService;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.repository.TripRepository;
import com.routick.domain.user.dto.LocationUpdateRequest;
import com.routick.domain.user.dto.UserResponse;
import com.routick.domain.user.entity.ProfileImage;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.ProfileImageRepository;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final TokenService tokenService;
    private final ProfileImageRepository profileImageRepository;

    // 내 정보 조회
    @Transactional(readOnly = true)
    public UserResponse getMe() {
        return UserResponse.from(getCurrentUser());
    }

    // 내 정보 수정 (닉네임·프로필 이미지)
    @Transactional
    public UserResponse updateMe(String nickname, MultipartFile profileImage) {
        User user = getCurrentUser();

        if (nickname != null && (nickname.length() < 2 || nickname.length() > 10)) {
            throw new CustomException(ErrorCode.INVALID_NICKNAME);
        }

        String profileImageUrl = null;
        if (profileImage != null && !profileImage.isEmpty()) {
            try {
                byte[] data = profileImage.getBytes();
                String contentType = profileImage.getContentType() != null
                        ? profileImage.getContentType() : "application/octet-stream";

                profileImageRepository.findById(user.getId())
                        .ifPresentOrElse(
                                existing -> existing.update(data, contentType),
                                () -> profileImageRepository.save(ProfileImage.of(user.getId(), data, contentType))
                        );
                profileImageUrl = "/images/profile/" + user.getId();
            } catch (IOException e) {
                throw new CustomException(ErrorCode.IMAGE_UPLOAD_FAILED);
            }
        }

        user.updateProfile(nickname, profileImageUrl);
        return UserResponse.from(user);
    }

    @Transactional
    public void deleteMe() {
        User user = getCurrentUser();

        tripRepository.deleteAll(tripRepository.findAllByUserIdOrderByCreatedAtDesc(user.getId()));
        preferenceRepository.deleteAll(preferenceRepository.findAllByUserId(user.getId()));
        profileImageRepository.deleteById(user.getId());   // 고아 이미지 row 정리
        userRepository.delete(user);

        tokenService.deleteRefreshToken(user.getId());
    }

    // 마지막 선택 위치 저장
    @Transactional
    public void updateLocation(LocationUpdateRequest request) {
        getCurrentUser().updateLastLocation(request.regionName(), request.lat(), request.lng());
    }

    private User getCurrentUser() {
        return userRepository.findById(SecurityUtil.getCurrentUserId())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }
}