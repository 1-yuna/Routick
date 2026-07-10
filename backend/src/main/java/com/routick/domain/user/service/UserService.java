package com.routick.domain.user.service;

import com.routick.domain.auth.service.TokenService;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.repository.TripRepository;
import com.routick.domain.user.dto.LocationUpdateRequest;
import com.routick.domain.user.dto.UserResponse;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import com.routick.global.util.FileStore;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final TokenService tokenService;
    private final FileStore fileStore;

    // 내 정보 조회
    @Transactional(readOnly = true)
    public UserResponse getMe() {
        return UserResponse.from(getCurrentUser());
    }

    // 내 정보 수정 (닉네임·프로필 이미지)
    @Transactional
    public UserResponse updateMe(String nickname, MultipartFile profileImage) {
        User user = getCurrentUser();

        // 닉네임이 온 경우에만 형식 검증
        if (nickname != null && (nickname.length() < 2 || nickname.length() > 10)) {
            throw new CustomException(ErrorCode.INVALID_NICKNAME);
        }

        String profileImageUrl = (profileImage != null && !profileImage.isEmpty())
                ? fileStore.save(profileImage)
                : null;

        user.updateProfile(nickname, profileImageUrl);   // 변경 감지로 UPDATE
        return UserResponse.from(user);
    }

    // 회원 탈퇴: 연관 데이터(여행 → 선호도) 삭제 후 계정 삭제
    @Transactional
    public void deleteMe() {
        User user = getCurrentUser();

        // FK 순서상 trips(→ preference 참조)부터 삭제
        tripRepository.deleteAll(tripRepository.findAllByUserIdOrderByCreatedAtDesc(user.getId()));
        preferenceRepository.deleteAll(preferenceRepository.findAllByUserId(user.getId()));
        userRepository.delete(user);

        // 토큰 무효화 (쿠키 만료는 컨트롤러에서)
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