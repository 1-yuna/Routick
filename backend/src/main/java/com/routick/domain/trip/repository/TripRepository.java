package com.routick.domain.trip.repository;

import com.routick.domain.trip.entity.Trip;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TripRepository extends JpaRepository<Trip, Long> {

    // 목록 조회 시 preference까지 한 번에 로딩 (N+1 방지)
    @EntityGraph(attributePaths = {"preference"})
    List<Trip> findAllByUserIdOrderByCreatedAtDesc(Long userId);
}