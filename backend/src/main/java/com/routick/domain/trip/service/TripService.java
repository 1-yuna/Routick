package com.routick.domain.trip.service;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.enums.Companion;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.dto.TripCreateRequest;
import com.routick.domain.trip.dto.TripCreateResponse;
import com.routick.domain.trip.dto.TripDaysUpdateRequest;
import com.routick.domain.trip.dto.TripListResponse;
import com.routick.domain.trip.entity.Trip;
import com.routick.domain.trip.entity.TripDay;
import com.routick.domain.trip.entity.TripPlace;
import com.routick.domain.trip.entity.enums.BlockType;
import com.routick.domain.trip.entity.enums.Bucket;
import com.routick.domain.trip.entity.enums.PlaceStatus;
import com.routick.domain.trip.repository.TripRepository;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class TripService {

    // ── 한국어 라벨 변환표 ─────────────────────────────────────

    private static final Map<Integer, String> PERIOD_LABELS = Map.of(
            1, "당일치기", 2, "1박2일", 3, "2박3일", 4, "3박4일");

    private static final Map<Companion, String> COMPANION_LABELS = Map.of(
            Companion.SOLO, "혼자", Companion.COUPLE, "연인", Companion.FRIEND, "친구",
            Companion.PARENTS, "부모님과", Companion.CHILDREN, "자녀와", Companion.PET, "반려동물과");

    private static final Map<String, String> MOOD_LABELS = Map.of(
            "active", "활기찬", "healing", "힐링", "sensibility", "감성",
            "quiet", "조용한", "warm", "따뜻한", "romantic", "로맨틱",
            "clean", "깔끔한", "vintage", "빈티지", "hip", "힙한");

    private static final Map<String, String> ACTIVITY_LABELS = Map.of(
            "exhibition", "전시/예술", "performance", "공연/문화", "activity", "액티비티",
            "indoor", "실내오락", "shopping", "쇼핑", "workshop", "공방/소품",
            "nature", "자연/관광", "bar", "술/바");

    private static final int MAX_TAGS = 3;

    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final UserRepository userRepository;

    // ── API ───────────────────────────────────────────────────

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
                .coverImageUrl(resolveCoverImage(request))
                .transport(toEnum(Transport.class, request.getTransport()))
                .region(request.getRegion())
                .startRegion(request.getStartRegion())
                .endRegion(request.getEndRegion())
                .build();

        request.getDays().forEach(d -> trip.getDays().add(buildDay(trip, d)));

        Trip saved = tripRepository.save(trip);   // cascade로 days, places까지 저장
        return new TripCreateResponse(saved.getId());
    }

    // 여행 일정 수정 (전체 교체) — 편집 완료 시
    @Transactional
    public void updateTripDays(Long tripId, TripDaysUpdateRequest request) {
        Trip trip = getOwnedTrip(tripId);

        trip.getDays().clear();   // orphanRemoval로 기존 trip_days/trip_places 삭제
        request.getDays().forEach(d -> trip.getDays().add(buildDay(trip, d)));
        // 변경 감지로 트랜잭션 종료 시 반영
    }

    // 내 여행 목록 조회 (최신순)
    @Transactional(readOnly = true)
    public TripListResponse getTrips() {
        List<TripListResponse.TripSummary> summaries =
                tripRepository.findAllByUserIdOrderByCreatedAtDesc(SecurityUtil.getCurrentUserId())
                        .stream()
                        .map(this::toSummary)
                        .toList();

        return new TripListResponse(summaries);
    }

    // ── 조회·검증 헬퍼 ─────────────────────────────────────────

    // 현재 로그인 사용자 조회
    private User getCurrentUser() {
        return userRepository.findById(SecurityUtil.getCurrentUserId())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }

    // 여행 조회 + 본인 소유 검증
    private Trip getOwnedTrip(Long tripId) {
        Trip trip = tripRepository.findById(tripId)
                .orElseThrow(() -> new CustomException(ErrorCode.TRIP_NOT_FOUND));

        if (!trip.getUser().getId().equals(SecurityUtil.getCurrentUserId())) {
            throw new CustomException(ErrorCode.FORBIDDEN);
        }
        return trip;
    }

    // ── 변환 헬퍼 (요청 → 엔티티) ──────────────────────────────

    // day 하나 조립 (저장·일정교체 공용)
    private TripDay buildDay(Trip trip, TripCreateRequest.DayDto dayDto) {
        TripDay day = TripDay.builder()
                .trip(trip)
                .dayNumber(dayDto.getDayNumber())
                .build();

        // start 블록 (block_order = 0)
        if (dayDto.getStart() != null) {
            day.getPlaces().add(toEndpointPlace(day, dayDto.getStart(), BlockType.START, 0));
        }

        int maxOrder = 0;
        for (TripCreateRequest.BlockDto b : dayDto.getBlocks()) {
            day.getPlaces().add(toBlockPlace(day, b));
            maxOrder = Math.max(maxOrder, b.getBlockOrder());
        }

        // end 블록 (block_order = 마지막 + 1)
        if (dayDto.getEnd() != null) {
            day.getPlaces().add(toEndpointPlace(day, dayDto.getEnd(), BlockType.END, maxOrder + 1));
        }

        return day;
    }

    // start/end → TripPlace
    private TripPlace toEndpointPlace(TripDay day, TripCreateRequest.EndpointDto e, BlockType type, int blockOrder) {
        TripCreateRequest.TransportDto exit = e.getExitTransport();
        TripCreateRequest.TransportDto enter = e.getEnterTransport();

        return TripPlace.builder()
                .tripDay(day)
                .type(type)
                .blockOrder(blockOrder)
                .placeId(e.getPlaceId())
                .name(e.getName())
                .address(e.getAddress())
                .lat(e.getLat())
                .lng(e.getLng())
                .transportToNext(exit != null ? toEnum(Transport.class, exit.getMode()) : null)
                .travelMinutesToNext(exit != null ? exit.getMinutes() : null)
                .enterTransportMode(enter != null ? toEnum(Transport.class, enter.getMode()) : null)
                .enterTransportMinutes(enter != null ? enter.getMinutes() : null)
                .build();
    }

    // blocks[] → TripPlace
    private TripPlace toBlockPlace(TripDay day, TripCreateRequest.BlockDto b) {
        BlockType type = switch (b.getType()) {
            case "place" -> BlockType.PLACE;
            case "walk" -> BlockType.WALK;
            case "parking" -> BlockType.PARKING;
            default -> throw new CustomException(ErrorCode.INVALID_INPUT);
        };

        TripCreateRequest.TransportDto exit = b.getExitTransport();
        TripCreateRequest.TransportDto enter = b.getEnterTransport();

        return TripPlace.builder()
                .tripDay(day)
                .type(type)
                .blockOrder(b.getBlockOrder())
                .placeOrder(b.getPlaceOrder())
                .placeId(b.getPlaceId())
                .name(b.getName())
                .address(b.getAddress())
                .lat(b.getLat())
                .lng(b.getLng())
                .bucket(toEnumOrNull(Bucket.class, b.getBucket()))
                .imageUrl(b.getImageUrl())
                .status(toEnumOrNull(PlaceStatus.class, b.getStatus()))
                .description(b.getDescription())
                .stayMinutes(b.getStayMinutes())
                .minutes(b.getMinutes())
                .arriveTime(parseTime(b.getArriveTime()))
                .leaveTime(parseTime(b.getLeaveTime()))
                .transportToNext(exit != null ? toEnum(Transport.class, exit.getMode()) : null)
                .travelMinutesToNext(exit != null ? exit.getMinutes() : null)
                .enterTransportMode(enter != null ? toEnum(Transport.class, enter.getMode()) : null)
                .enterTransportMinutes(enter != null ? enter.getMinutes() : null)
                .build();
    }

    // 커버 이미지: 미입력 시 첫 place 블록 이미지
    private String resolveCoverImage(TripCreateRequest request) {
        if (request.getCoverImageUrl() != null) return request.getCoverImageUrl();
        return request.getDays().stream()
                .flatMap(d -> d.getBlocks().stream())
                .filter(b -> "place".equals(b.getType()) && b.getImageUrl() != null)
                .map(TripCreateRequest.BlockDto::getImageUrl)
                .findFirst()
                .orElse(null);
    }

    // ── 변환 헬퍼 (엔티티 → 응답) ──────────────────────────────

    // Trip → 목록 카드 요약
    private TripListResponse.TripSummary toSummary(Trip trip) {
        Preference p = trip.getPreference();

        return new TripListResponse.TripSummary(
                trip.getId(),
                trip.getTitle(),
                trip.getCoverImageUrl(),
                toRegionLabel(trip),
                trip.getTransport().name().toLowerCase(),
                PERIOD_LABELS.getOrDefault(p.getTravelDays(), "당일치기"),
                COMPANION_LABELS.get(p.getCompanion()),
                toTags(p),
                trip.getCreatedAt()
        );
    }

    // 지역 라벨: only면 "홍대", endpoint면 "홍대 → 부산"
    private String toRegionLabel(Trip trip) {
        return trip.getRegion() != null
                ? trip.getRegion()
                : trip.getStartRegion() + " → " + trip.getEndRegion();
    }

    // 태그: 분위기 + 활동 한국어 라벨, 최대 3개
    private List<String> toTags(Preference p) {
        Stream<String> moods = p.getMoods() == null ? Stream.empty()
                : p.getMoods().stream().map(m -> MOOD_LABELS.getOrDefault(m, m));
        Stream<String> activities = p.getActivities() == null ? Stream.empty()
                : p.getActivities().stream().map(a -> ACTIVITY_LABELS.getOrDefault(a, a));

        return Stream.concat(moods, activities).limit(MAX_TAGS).toList();
    }

    // ── 공통 유틸 ──────────────────────────────────────────────

    private LocalTime parseTime(String time) {
        if (time == null || time.isBlank()) return null;
        try {
            return LocalTime.parse(time);
        } catch (Exception e) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }
    }

    // 필수 enum: 불일치 시 INVALID_INPUT
    private <T extends Enum<T>> T toEnum(Class<T> type, String value) {
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }
    }

    // 선택 enum: 모르는 값이면 null
    private <T extends Enum<T>> T toEnumOrNull(Class<T> type, String value) {
        if (value == null) return null;
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }
}