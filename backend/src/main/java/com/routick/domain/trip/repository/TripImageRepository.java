package com.routick.domain.trip.repository;

import com.routick.domain.trip.entity.TripImage;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TripImageRepository extends JpaRepository<TripImage, Long> {
}