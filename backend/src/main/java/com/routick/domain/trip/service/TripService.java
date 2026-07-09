package com.routick.domain.trip.service;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.dto.*;
import com.routick.domain.trip.entity.Trip;
import com.routick.domain.trip.repository.TripRepository;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TripService {

    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final UserRepository userRepository;
    private final TripMapper tripMapper;

    // 여행 저장
    @Transactional
    public TripCreateResponse createTrip(TripCreateRequest request) {
        User user = getCurrentUser();

        Preference preference = preferenceRepository.findById(request.getPreferenceId())
                .orElseThrow(() -> new CustomException(ErrorCode.PREFERENCE_NOT_FOUND));

        if (!preference.getUser().getId().equals(user.getId())) {
            throw new CustomException(ErrorCode.FORBIDDEN);
        }

        Trip trip = Trip.builder()
                .user(user)
                .preference(preference)
                .title(request.getTitle())
                .coverImageUrl(tripMapper.resolveCoverImage(request))
                .transport(tripMapper.toTransport(request.getTransport()))
                .region(request.getRegion())
                .startRegion(request.getStartRegion())
                .endRegion(request.getEndRegion())
                .build();

        request.getDays().forEach(d -> trip.getDays().add(tripMapper.buildDay(trip, d)));

        Trip saved = tripRepository.save(trip);
        return new TripCreateResponse(saved.getId());
    }

    // 여행 일정 수정 (전체 교체) — 편집 완료 시
    @Transactional
    public void updateTripDays(Long tripId, TripDaysUpdateRequest request) {
        Trip trip = getOwnedTrip(tripId);

        trip.getDays().clear();
        request.getDays().forEach(d -> trip.getDays().add(tripMapper.buildDay(trip, d)));
    }

    // 내 여행 목록 조회 (최신순)
    @Transactional(readOnly = true)
    public TripListResponse getTrips() {
        List<TripListResponse.TripSummary> summaries =
                tripRepository.findAllByUserIdOrderByCreatedAtDesc(SecurityUtil.getCurrentUserId())
                        .stream()
                        .map(tripMapper::toSummary)
                        .toList();

        return new TripListResponse(summaries);
    }

    // 내 여행 상세 조회
    @Transactional(readOnly = true)
    public TripDetailResponse getTripDetail(Long tripId) {
        return tripMapper.toDetail(getOwnedTrip(tripId));
    }

    // ── 조회·검증 헬퍼 ──────────────────────────────────────────

    private User getCurrentUser() {
        return userRepository.findById(SecurityUtil.getCurrentUserId())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }

    private Trip getOwnedTrip(Long tripId) {
        Trip trip = tripRepository.findById(tripId)
                .orElseThrow(() -> new CustomException(ErrorCode.TRIP_NOT_FOUND));

        if (!trip.getUser().getId().equals(SecurityUtil.getCurrentUserId())) {
            throw new CustomException(ErrorCode.FORBIDDEN);
        }
        return trip;
    }
}