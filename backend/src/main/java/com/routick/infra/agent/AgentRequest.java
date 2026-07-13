package com.routick.infra.agent;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import com.routick.domain.course.entity.Preference;
import com.routick.domain.course.entity.PreferenceDay;
import com.routick.domain.course.entity.enums.RouteType;

import java.util.List;

// Spring → AI 요청 (직렬화 시 snake_case: routeType → route_type)
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
@JsonInclude(JsonInclude.Include.NON_NULL)
public record AgentRequest(
        String routeType,
        Integer travelDays,
        String travelDate,
        String transport,
        Double lat,
        Double lng,
        List<AgentDay> days,
        String companion,
        List<String> moods,
        List<String> activities,
        List<String> avoidActivities,
        String startTime,
        String endTime
) {
    public static AgentRequest from(Preference p) {
        boolean isOnly = p.getRouteType() == RouteType.ONLY;
        return new AgentRequest(
                p.getRouteType().name().toLowerCase(),
                p.getTravelDays(),
                p.getTravelDate().toString(),
                p.getTransport().name().toLowerCase(),
                isOnly ? p.getLat() : null,
                isOnly ? p.getLng() : null,
                isOnly ? null : p.getDays().stream().map(AgentDay::from).toList(),
                p.getCompanion().name().toLowerCase(),
                p.getMoods(),
                p.getActivities(),
                p.getAvoidActivities(),
                "11:00",
                "22:00"
        );
    }

    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record AgentDay(
            Integer dayNumber,
            Double startLat, Double startLng, String startName, String startAddress, String startPlaceId,
            Double midLat, Double midLng, String midName,
            Double endLat, Double endLng, String endName, String endAddress, String endPlaceId
    ) {
        public static AgentDay from(PreferenceDay d) {
            return new AgentDay(
                    d.getDayNumber(),
                    d.getStartLat(), d.getStartLng(), d.getStartName(), d.getStartAddress(), d.getStartPlaceId(),
                    d.getMidLat(), d.getMidLng(), d.getMidName(),
                    d.getEndLat(), d.getEndLng(), d.getEndName(), d.getEndAddress(), d.getEndPlaceId()
            );
        }
    }
}