package com.routick.domain.course.repository;

import com.routick.domain.course.entity.Preference;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PreferenceRepository extends JpaRepository<Preference, Long> {

    // 사용자의 선호도 전체 조회 (회원 탈퇴 시 삭제용)
    List<Preference> findAllByUserId(Long userId);
}