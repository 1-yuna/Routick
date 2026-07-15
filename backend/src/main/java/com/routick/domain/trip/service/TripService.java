package com.routick.domain.trip.service;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.dto.*;
import com.routick.domain.trip.entity.Trip;
import com.routick.domain.trip.entity.TripDay;
import com.routick.domain.trip.entity.TripImage;
import com.routick.domain.trip.entity.TripPlace;
import com.routick.domain.trip.repository.TripImageRepository;
import com.routick.domain.trip.repository.TripRepository;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import com.routick.global.util.FileStore;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.Base64;
import java.util.List;

@Service
@RequiredArgsConstructor
public class TripService {

    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final UserRepository userRepository;
    private final TripImageRepository tripImageRepository;
    private final TripMapper tripMapper;
    private final FileStore fileStore;

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

        Trip saved = tripRepository.save(trip);   // 여기서 TripDay/TripPlace까지 cascade INSERT, id 생성됨

        saveTripImages(request.getDays(), saved.getDays());

        return new TripCreateResponse(saved.getId());
    }

    // 요청의 blocks[].imageData(base64)를 저장된 TripPlace.id로 TripImage에 저장하고 image_url 갱신
    // dayDtos와 days는 buildDay() 호출 순서와 동일한 순서로 쌍을 이룸
    private void saveTripImages(List<TripCreateRequest.DayDto> dayDtos, List<TripDay> days) {
        for (int i = 0; i < dayDtos.size(); i++) {
            TripCreateRequest.DayDto dayDto = dayDtos.get(i);
            TripDay day = days.get(i);

            int offset = dayDto.getStart() != null ? 1 : 0;   // start 행이 있으면 blocks는 1번 인덱스부터
            List<TripPlace> places = day.getPlaces();
            List<TripCreateRequest.BlockDto> blocks = dayDto.getBlocks();

            for (int j = 0; j < blocks.size(); j++) {
                TripCreateRequest.BlockDto b = blocks.get(j);
                if (b.getImageData() == null) continue;

                TripPlace place = places.get(offset + j);
                TripImage image = TripImage.of(place.getId(), decodeBase64(b.getImageData()), extractContentType(b.getImageData()));
                tripImageRepository.save(image);
                place.updateImageUrl("/images/trip/" + place.getId());
            }
        }
    }

    // "data:image/png;base64,...." → 바이트
    private byte[] decodeBase64(String dataUrl) {
        try {
            String base64 = dataUrl.substring(dataUrl.indexOf(',') + 1);
            return Base64.getDecoder().decode(base64);
        } catch (Exception e) {
            throw new CustomException(ErrorCode.IMAGE_UPLOAD_FAILED);
        }
    }

    // "data:image/png;base64,...." → "image/png"
    private String extractContentType(String dataUrl) {
        try {
            return dataUrl.substring(5, dataUrl.indexOf(';'));
        } catch (Exception e) {
            return "application/octet-stream";
        }
    }

    // 여행 일정 수정 (전체 교체) — 편집 완료 시
    @Transactional
    public void updateTripDays(Long tripId, TripDaysUpdateRequest request) {
        Trip trip = getOwnedTrip(tripId);

        trip.getDays().clear();
        request.getDays().forEach(d -> trip.getDays().add(tripMapper.buildDay(trip, d)));
        // TODO: 일정 수정 배치 때 - 여기도 imageData 처리 추가 필요
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

    // 내 여행 수정 (제목·커버 이미지)
    @Transactional
    public TripUpdateResponse updateTrip(Long tripId, String title, MultipartFile coverImage) {
        Trip trip = getOwnedTrip(tripId);

        String coverImageUrl = (coverImage != null && !coverImage.isEmpty())
                ? fileStore.save(coverImage)
                : null;

        trip.updateInfo(title, coverImageUrl);

        return new TripUpdateResponse(trip.getId(), trip.getTitle(), trip.getCoverImageUrl());
    }

    // 내 여행 삭제
    @Transactional
    public void deleteTrip(Long tripId) {
        tripRepository.delete(getOwnedTrip(tripId));
    }
}