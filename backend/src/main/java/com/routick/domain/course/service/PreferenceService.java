package com.routick.domain.course.service;

import com.routick.domain.course.dto.PreferenceCreateRequest;
import com.routick.domain.course.dto.PreferenceCreateResponse;
import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.PreferenceDay;
import com.routick.domain.course.entity.enums.Companion;
import com.routick.domain.course.entity.enums.RouteType;
import com.routick.domain.course.entity.enums.Transport;
import com.routick.domain.course.repository.PreferenceRepository;
import com.routick.domain.user.entity.User;
import com.routick.domain.user.repository.UserRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import com.routick.global.security.SecurityUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class PreferenceService {

    private static final double WALK_LIMIT_KM = 3.0;
    private static final double CAR_LIMIT_KM = 20.0;

    private final PreferenceRepository preferenceRepository;
    private final UserRepository userRepository;

    // 선호도 저장
    @Transactional
    public PreferenceCreateResponse createPreference(PreferenceCreateRequest request) {
        User user = userRepository.findById(SecurityUtil.getCurrentUserId())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        RouteType routeType = toEnum(RouteType.class, request.getRouteType());
        Transport transport = toEnum(Transport.class, request.getTransport());
        Companion companion = toEnum(Companion.class, request.getCompanion());

        validateByRouteType(routeType, transport, request);

        Preference preference = Preference.builder()
                .user(user)
                .routeType(routeType)
                .travelDays(request.getTravelDays())
                .travelDate(request.getTravelDate())
                .transport(transport)
                .destination(request.getDestination())
                .lat(request.getLat())
                .lng(request.getLng())
                .companion(companion)
                .moods(request.getMoods())
                .activities(request.getActivities())
                .avoidActivities(request.getAvoidActivities())
                .build();

        if (routeType == RouteType.ENDPOINT) {
            request.getDays().forEach(d -> preference.getDays().add(
                    PreferenceDay.builder()
                            .preference(preference)
                            .dayNumber(d.getDayNumber())
                            .startLat(d.getStartLat()).startLng(d.getStartLng())
                            .startName(d.getStartName()).startAddress(d.getStartAddress())
                            .startPlaceId(d.getStartPlaceId())
                            .midLat(d.getMidLat()).midLng(d.getMidLng()).midName(d.getMidName())
                            .endLat(d.getEndLat()).endLng(d.getEndLng())
                            .endName(d.getEndName()).endAddress(d.getEndAddress())
                            .endPlaceId(d.getEndPlaceId())
                            .build()));
        }

        Preference saved = preferenceRepository.save(preference);
        return new PreferenceCreateResponse(saved.getId());
    }

    // routeType별 필수값 + 거리 검증
    private void validateByRouteType(RouteType routeType, Transport transport, PreferenceCreateRequest request) {
        if (routeType == RouteType.ONLY) {
            if (request.getDestination() == null || request.getLat() == null || request.getLng() == null) {
                throw new CustomException(ErrorCode.INVALID_INPUT);
            }
            return;
        }

        // ENDPOINT: days 필수, 개수 = travelDays
        if (request.getDays() == null || request.getDays().size() != request.getTravelDays()) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }

        // day별 출발-도착 직선거리 검증 (도보 3km / 자동차 20km)
        double limitKm = (transport == Transport.WALK) ? WALK_LIMIT_KM : CAR_LIMIT_KM;
        for (PreferenceCreateRequest.DayRequest day : request.getDays()) {
            double distance = haversineKm(day.getStartLat(), day.getStartLng(), day.getEndLat(), day.getEndLng());
            if (distance > limitKm) {
                throw new CustomException(ErrorCode.DISTANCE_EXCEEDED);
            }
        }
    }

    // 문자열 → enum 변환 (불일치 시 INVALID_INPUT)
    private <T extends Enum<T>> T toEnum(Class<T> type, String value) {
        try {
            return Enum.valueOf(type, value.toUpperCase());
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new CustomException(ErrorCode.INVALID_INPUT);
        }
    }

    // 두 좌표 간 직선거리 (km)
    private double haversineKm(double lat1, double lng1, double lat2, double lng2) {
        double r = 6371;
        double dLat = Math.toRadians(lat2 - lat1);
        double dLng = Math.toRadians(lng2 - lng1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        return r * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }
}