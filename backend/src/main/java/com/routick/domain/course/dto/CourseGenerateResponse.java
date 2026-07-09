package com.routick.domain.course.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

// AI 응답 수신 + 프론트 응답 겸용 DTO
// 수신: AgentApiClient의 snake 매퍼가 image_url → imageUrl로 매핑
// 송신: 기본 매퍼가 camelCase로 직렬화
@Getter
@Setter
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CourseGenerateResponse {

    private Long preferenceId;    // AI 응답엔 없음 → 서비스에서 세팅
    private String transport;
    private Meta meta;
    private String region;        // routeType=only만
    private String startRegion;   // routeType=endpoint만
    private String endRegion;
    private List<Day> days;

    @Getter @Setter @NoArgsConstructor
    public static class Meta {
        private String period;
        private String date;
        private String companion;
        private List<String> mood;
        private List<String> activity;
        private List<String> dislike;
    }

    @Getter @Setter @NoArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class Day {
        private Integer dayNumber;
        private Endpoint start;   // endpoint만
        private Endpoint end;
        private List<Block> blocks;
    }

    @Getter @Setter @NoArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class Endpoint {
        private String name;
        private String address;
        private Double lat;
        private Double lng;
        private String placeId;
        private TransportInfo enterTransport;
        private TransportInfo exitTransport;
    }

    @Getter @Setter @NoArgsConstructor
    public static class TransportInfo {
        private String mode;
        private Integer minutes;
    }

    @Getter @Setter @NoArgsConstructor
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class Block {
        private Integer blockOrder;
        private String type;          // place / walk / parking
        private String bucket;
        private Integer placeOrder;
        private String placeId;
        private String name;
        private String address;
        private Double lat;
        private Double lng;
        private String imageUrl;
        private String status;        // AI: "영업 중" → 변환 후: OPEN
        private String description;
        private Integer stayMinutes;
        private Integer minutes;      // walk만
        private String arriveTime;
        private String leaveTime;
        private TransportInfo enterTransport;   // parking만
        private TransportInfo exitTransport;
    }
}