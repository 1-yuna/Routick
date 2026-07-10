package com.routick.domain.user.controller;

import com.routick.domain.user.dto.LocationUpdateRequest;
import com.routick.domain.user.dto.UserResponse;
import com.routick.domain.user.service.UserService;
import com.routick.global.response.ApiResponse;
import com.routick.global.util.CookieUtil;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    // 내 정보 조회 (스플래시의 로그인 상태 확인 겸용)
    @GetMapping("/me")
    public ApiResponse<UserResponse> getMe() {
        return ApiResponse.success(userService.getMe());
    }

    // 내 정보 수정 (multipart: nickname + profileImage)
    @PatchMapping("/me")
    public ApiResponse<UserResponse> updateMe(
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) MultipartFile profileImage) {
        return ApiResponse.success("정보가 수정되었습니다.", userService.updateMe(nickname, profileImage));
    }

    // 회원 탈퇴 (계정·데이터 삭제 + 쿠키 만료)
    @DeleteMapping("/me")
    public ApiResponse<Void> deleteMe(HttpServletResponse response) {
        userService.deleteMe();
        CookieUtil.expireTokenCookie(response, "accessToken");
        CookieUtil.expireTokenCookie(response, "refreshToken");
        return ApiResponse.success("탈퇴가 완료되었습니다.");
    }

    // 마지막 위치 저장 (홈 지역 드롭다운 선택 시)
    @PatchMapping("/me/location")
    public ApiResponse<Void> updateLocation(@Valid @RequestBody LocationUpdateRequest request) {
        userService.updateLocation(request);
        return ApiResponse.success("위치가 저장되었습니다.");
    }
}