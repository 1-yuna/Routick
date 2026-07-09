package com.routick.domain.trip.service;

import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.trip.dto.TripCreateRequest;
import com.routick.domain.trip.dto.TripCreateResponse;
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

@Service
@RequiredArgsConstructor
public class TripService {

    private final TripRepository tripRepository;
    private final PreferenceRepository preferenceRepository;
    private final UserRepository userRepository;

    // 여행 저장
    @Transactional
    public TripCreateResponse createTrip(TripCreateRequest request) {
        User user = userRepository.findById(SecurityUtil.getCurrentUserId())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

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

        for (TripCreateRequest.DayDto dayDto : request.getDays()) {
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

            trip.getDays().add(day);
        }

        Trip saved = tripRepository.save(trip);   // cascade로 days, places까지 저장
        return new TripCreateResponse(saved.getId());
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

    // 선택 enum: 모르는 값이면 null (bucket "parking" 등)
    private <T extends Enum<T>> T toEnumOrNull(Class<T> type, String value) {
        if (value == null) return null;
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }
}