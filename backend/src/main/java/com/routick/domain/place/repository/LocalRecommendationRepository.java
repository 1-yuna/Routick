package com.routick.domain.place.repository;

import com.routick.domain.place.entity.LocalRecommendation;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface LocalRecommendationRepository extends JpaRepository<LocalRecommendation, Long> {

    // 지역명으로 캐시 조회
    Optional<LocalRecommendation> findByRegionName(String regionName);
}