package com.routick.domain.place.repository;

import com.routick.domain.place.entity.PlaceCacheArea;
import com.routick.domain.place.entity.enums.Category;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PlaceCacheAreaRepository extends JpaRepository<PlaceCacheArea, Long> {

    // 지역+카테고리로 캐시 조회
    Optional<PlaceCacheArea> findByRegionNameAndCategory(String regionName, Category category);
}