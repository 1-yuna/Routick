package com.routick.domain.place.repository;

import com.routick.domain.place.entity.PlaceCacheItem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PlaceCacheItemRepository extends JpaRepository<PlaceCacheItem, Long> {

    // 카카오 placeId로 조회 (여러 지역 캐시에 중복 저장됐을 수 있어 첫 건만)
    Optional<PlaceCacheItem> findFirstByPlaceId(String placeId);
}