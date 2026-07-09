package com.routick.domain.trip.service;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.enums.Companion;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.trip.dto.*;
import com.routick.domain.trip.entity.Trip;
import com.routick.domain.trip.entity.TripDay;
import com.routick.domain.trip.entity.TripPlace;
import com.routick.domain.trip.entity.enums.BlockType;
import com.routick.domain.trip.entity.enums.Bucket;
import com.routick.domain.trip.entity.enums.PlaceStatus;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import org.springframework.stereotype.Component;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

// Trip 도메인의 DTO ↔ 엔티티 변환 전담
// - 요청 → 엔티티: 저장/일정교체 시 days JSON을 TripDay/TripPlace로 변환
// - 엔티티 → 응답: 목록 카드 요약, 상세 타임라인 복원, 한국어 라벨 변환
@Component
public class TripMapper {

    private static final int MAX_TAGS = 3;                    // 목록 카드 태그 최대 개수
    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm");

    // 여행 기간 라벨 (travelDays → 한국어)
    private static final Map<Integer, String> PERIOD_LABELS = Map.of(
            1, "당일치기", 2, "1박2일", 3, "2박3일", 4, "3박4일");

    // 동행 유형 라벨 (enum → 한국어)
    private static final Map<Companion, String> COMPANION_LABELS = Map.of(
            Companion.SOLO, "혼자", Companion.COUPLE, "연인", Companion.FRIEND, "친구",
            Companion.PARENTS, "부모님과", Companion.CHILDREN, "자녀와", Companion.PET, "반려동물과");

    // 분위기 라벨 (영어 값 → 한국어)
    private static final Map<String, String> MOOD_LABELS = Map.of(
            "active", "활기찬", "healing", "힐링", "sensibility", "감성",
            "quiet", "조용한", "warm", "따뜻한", "romantic", "로맨틱",
            "clean", "깔끔한", "vintage", "빈티지", "hip", "힙한");

    // 활동 라벨 (영어 값 → 한국어)
    private static final Map<String, String> ACTIVITY_LABELS = Map.of(
            "exhibition", "전시/예술", "performance", "공연/문화", "activity", "액티비티",
            "indoor", "실내오락", "shopping", "쇼핑", "workshop", "공방/소품",
            "nature", "자연/관광", "bar", "술/바");

    // ── 요청 → 엔티티 ──────────────────────────────────────────

    // day 하나 조립 (여행 저장·일정 교체 공용)
    // start는 block_order=0, blocks는 요청 순서 그대로, end는 마지막+1로 flatten
    public TripDay buildDay(Trip trip, TripCreateRequest.DayDto dayDto) {
        TripDay day = TripDay.builder()
                .trip(trip)
                .dayNumber(dayDto.getDayNumber())
                .build();

        // start 블록 (endpoint 케이스만 존재)
        if (dayDto.getStart() != null) {
            day.getPlaces().add(toEndpointPlace(day, dayDto.getStart(), BlockType.START, 0));
        }

        // 일반 블록 (place/walk/parking)
        int maxOrder = 0;
        for (TripCreateRequest.BlockDto b : dayDto.getBlocks()) {
            day.getPlaces().add(toBlockPlace(day, b));
            maxOrder = Math.max(maxOrder, b.getBlockOrder());
        }

        // end 블록 (endpoint 케이스만 존재)
        if (dayDto.getEnd() != null) {
            day.getPlaces().add(toEndpointPlace(day, dayDto.getEnd(), BlockType.END, maxOrder + 1));
        }

        return day;
    }

    // 커버 이미지 결정: 프론트가 보낸 값 > 첫 place 블록 이미지 > null
    public String resolveCoverImage(TripCreateRequest request) {
        if (request.getCoverImageUrl() != null) return request.getCoverImageUrl();
        return request.getDays().stream()
                .flatMap(d -> d.getBlocks().stream())
                .filter(b -> "place".equals(b.getType()) && b.getImageUrl() != null)
                .map(TripCreateRequest.BlockDto::getImageUrl)
                .findFirst()
                .orElse(null);
    }

    // "walk"/"car" 문자열 → Transport enum
    public Transport toTransport(String value) {
        return toEnum(Transport.class, value);
    }

    // ── 엔티티 → 목록 응답 ─────────────────────────────────────

    // Trip → 내 여행 목록 카드 요약 (지역 라벨·기간·동행·태그 한국어 변환 포함)
    public TripListResponse.TripSummary toSummary(Trip trip) {
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

    // ── 엔티티 → 상세 응답 ─────────────────────────────────────

    // Trip → 상세 응답 (코스 생성 응답과 동일 구조로 복원)
    public TripDetailResponse toDetail(Trip trip) {
        Preference p = trip.getPreference();

        // 여행 메타 정보 (선호도 기반, 한국어 라벨)
        TripDetailResponse.Meta meta = new TripDetailResponse.Meta(
                PERIOD_LABELS.getOrDefault(p.getTravelDays(), "당일치기"),
                p.getTravelDate().toString(),
                COMPANION_LABELS.get(p.getCompanion()),
                mapLabels(p.getMoods(), MOOD_LABELS),
                mapLabels(p.getActivities(), ACTIVITY_LABELS),
                p.getAvoidActivities() == null ? List.of() : p.getAvoidActivities()
        );

        List<TripDetailResponse.DayDto> days = trip.getDays().stream()
                .sorted(Comparator.comparing(TripDay::getDayNumber))
                .map(this::toDayDto)
                .toList();

        return new TripDetailResponse(
                trip.getId(), trip.getTitle(), trip.getCoverImageUrl(),
                trip.getTransport().name().toLowerCase(), meta,
                trip.getRegion(), trip.getStartRegion(), trip.getEndRegion(), days
        );
    }

    // ── 내부 헬퍼: 요청 → 엔티티 ───────────────────────────────

    // start/end 객체 → TripPlace 행 (좌표·placeId + 들어오는/나가는 이동 정보)
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

    // blocks[] 항목 → TripPlace 행 (place/walk/parking 타입별 필드 매핑)
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

    // ── 내부 헬퍼: 엔티티 → 응답 ───────────────────────────────

    // TripDay → DayDto: 저장 때 flatten한 행들을 원래 구조로 복원
    // (START 행 → start 객체, END 행 → end 객체, 나머지 → blocks 배열)
    private TripDetailResponse.DayDto toDayDto(TripDay day) {
        List<TripPlace> sorted = day.getPlaces().stream()
                .sorted(Comparator.comparing(TripPlace::getBlockOrder))
                .toList();

        TripDetailResponse.EndpointDto start = null;
        TripDetailResponse.EndpointDto end = null;
        List<TripDetailResponse.BlockDto> blocks = new ArrayList<>();

        for (TripPlace tp : sorted) {
            switch (tp.getType()) {
                case START -> start = toEndpointDto(tp);
                case END -> end = toEndpointDto(tp);
                default -> blocks.add(toBlockDto(tp));
            }
        }

        return new TripDetailResponse.DayDto(day.getDayNumber(), start, end, blocks);
    }

    // START/END 행 → start/end 객체
    private TripDetailResponse.EndpointDto toEndpointDto(TripPlace tp) {
        return new TripDetailResponse.EndpointDto(
                tp.getName(), tp.getAddress(), tp.getLat(), tp.getLng(), tp.getPlaceId(),
                toTransportDto(tp.getEnterTransportMode(), tp.getEnterTransportMinutes()),
                toTransportDto(tp.getTransportToNext(), tp.getTravelMinutesToNext())
        );
    }

    // PLACE/WALK/PARKING 행 → blocks 항목
    private TripDetailResponse.BlockDto toBlockDto(TripPlace tp) {
        return new TripDetailResponse.BlockDto(
                tp.getBlockOrder(),
                tp.getType().name().toLowerCase(),
                tp.getBucket() != null ? tp.getBucket().name().toLowerCase() : null,
                tp.getPlaceOrder(), tp.getPlaceId(), tp.getName(), tp.getAddress(),
                tp.getLat(), tp.getLng(), tp.getImageUrl(),
                tp.getStatus() != null ? tp.getStatus().name() : null,
                tp.getDescription(), tp.getStayMinutes(), tp.getMinutes(),
                formatTime(tp.getArriveTime()), formatTime(tp.getLeaveTime()),
                toTransportDto(tp.getEnterTransportMode(), tp.getEnterTransportMinutes()),
                toTransportDto(tp.getTransportToNext(), tp.getTravelMinutesToNext())
        );
    }

    // 이동 정보 → { mode, minutes } (없으면 null → 응답에서 제외)
    private TripDetailResponse.TransportDto toTransportDto(Transport mode, Integer minutes) {
        return mode == null ? null : new TripDetailResponse.TransportDto(mode.name().toLowerCase(), minutes);
    }

    // 지역 라벨: only면 "홍대", endpoint면 "홍대 → 부산"
    private String toRegionLabel(Trip trip) {
        return trip.getRegion() != null
                ? trip.getRegion()
                : trip.getStartRegion() + " → " + trip.getEndRegion();
    }

    // 목록 카드 태그: 분위기 + 활동 한국어 라벨, 최대 MAX_TAGS개
    private List<String> toTags(Preference p) {
        Stream<String> moods = p.getMoods() == null ? Stream.empty()
                : p.getMoods().stream().map(m -> MOOD_LABELS.getOrDefault(m, m));
        Stream<String> activities = p.getActivities() == null ? Stream.empty()
                : p.getActivities().stream().map(a -> ACTIVITY_LABELS.getOrDefault(a, a));

        return Stream.concat(moods, activities).limit(MAX_TAGS).toList();
    }

    // ── 내부 헬퍼: 공통 유틸 ───────────────────────────────────

    // 영어 값 리스트 → 한국어 라벨 리스트 (매핑 없으면 원본 유지)
    private List<String> mapLabels(List<String> values, Map<String, String> labels) {
        return values == null ? List.of()
                : values.stream().map(v -> labels.getOrDefault(v, v)).toList();
    }

    // LocalTime → "HH:mm" 문자열
    private String formatTime(LocalTime time) {
        return time == null ? null : time.format(TIME_FORMAT);
    }

    // "HH:mm" 문자열 → LocalTime (형식 오류 시 INVALID_INPUT)
    private LocalTime parseTime(String time) {
        if (time == null || time.isBlank()) return null;
        try {
            return LocalTime.parse(time);
        } catch (Exception e) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }
    }

    // 필수 enum 변환: 불일치 시 INVALID_INPUT
    private <T extends Enum<T>> T toEnum(Class<T> type, String value) {
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }
    }

    // 선택 enum 변환: 모르는 값이면 null (에러 대신 무시)
    private <T extends Enum<T>> T toEnumOrNull(Class<T> type, String value) {
        if (value == null) return null;
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }
}