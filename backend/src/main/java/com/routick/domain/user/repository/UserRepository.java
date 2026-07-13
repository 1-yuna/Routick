package com.routick.domain.user.repository;

import com.routick.domain.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    // 이메일로 사용자 조회 (가입 여부·가입 수단 확인용)
    Optional<User> findByEmail(String email);
}