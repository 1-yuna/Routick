package com.routick.domain.user.controller;

import com.routick.domain.user.dto.LocationUpdateRequest;
import com.routick.domain.user.dto.UserResponse;
import com.routick.domain.user.service.UserService;
import com.routick.global.response.ApiResponse;
import com.routick.global.util.CookieUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "User", description = "내 정보 관리")
public class UserController {

    private final UserService userService;

    // 내 정보 조회 (스플래시의 로그인 상태 확인 겸용)
    @Operation(summary = "내 정보 조회", description = "로그인 사용자의 정보를 조회한다 (스플래시 로그인 상태 확인 겸용)")
    @GetMapping("/me")
    public ApiResponse<UserResponse> getMe() {
        return ApiResponse.success(userService.getMe());
    }

    // 내 정보 수정 (multipart: nickname + profileImage)
    @Operation(summary = "내 정보 수정", description = "닉네임·프로필 이미지를 수정한다 (multipart/form-data)")
    @PatchMapping("/me")
    public ApiResponse<UserResponse> updateMe(
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) MultipartFile profileImage) {
        return ApiResponse.success("정보가 수정되었습니다.", userService.updateMe(nickname, profileImage));
    }

    // 회원 탈퇴 (계정·데이터 삭제 + 쿠키 만료)
    @Operation(summary = "회원 탈퇴", description = "계정과 연관 데이터(여행·선호도)를 삭제하고 쿠키를 만료한다")
    @DeleteMapping("/me")
    public ApiResponse<Void> deleteMe(HttpServletResponse response) {
        userService.deleteMe();
        CookieUtil.expireTokenCookie(response, "accessToken");
        CookieUtil.expireTokenCookie(response, "refreshToken");
        return ApiResponse.success("탈퇴가 완료되었습니다.");
    }

    // 마지막 위치 저장 (홈 지역 드롭다운 선택 시)
    @Operation(summary = "마지막 위치 저장", description = "홈 지역 드롭다운 선택 시 지역명·좌표를 저장한다")
    @PatchMapping("/me/location")
    public ApiResponse<Void> updateLocation(@Valid @RequestBody LocationUpdateRequest request) {
        userService.updateLocation(request);
        return ApiResponse.success("위치가 저장되었습니다.");
    }
}