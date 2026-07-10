package com.routick.infra.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.routick.domain.user.entity.enums.Provider;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

// 소셜 로그인 3사와의 통신: 인가 URL 생성 → 토큰 교환 → 사용자 정보 조회
@Slf4j
@Component
@RequiredArgsConstructor
public class OAuthApiClient {

    private final OAuthProperties properties;
    private final RestClient restClient = RestClient.create();

    // 소셜 로그인 페이지 URL 생성 (사용자를 여기로 리다이렉트)
    public String buildAuthorizeUrl(Provider provider) {
        OAuthProperties.Registration config = getConfig(provider);
        return switch (provider) {
            case KAKAO -> "https://kauth.kakao.com/oauth/authorize"
                    + "?client_id=" + config.getClientId()
                    + "&redirect_uri=" + config.getRedirectUri()
                    + "&response_type=code";
            case NAVER -> "https://nid.naver.com/oauth2.0/authorize"
                    + "?client_id=" + config.getClientId()
                    + "&redirect_uri=" + config.getRedirectUri()
                    + "&response_type=code&state=routick";
            case GOOGLE -> "https://accounts.google.com/o/oauth2/v2/auth"
                    + "?client_id=" + config.getClientId()
                    + "&redirect_uri=" + config.getRedirectUri()
                    + "&response_type=code&scope=email%20profile";
            default -> throw new CustomException(ErrorCode.OAUTH_FAILED);
        };
    }

    // 인가코드 → 사용자 정보 (토큰 교환 + 조회 통합)
    public OAuthUserInfo fetchUserInfo(Provider provider, String code) {
        try {
            String accessToken = requestToken(provider, code);
            return requestUserInfo(provider, accessToken);
        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            log.error("소셜 사용자 정보 조회 실패: {}", provider, e);
            throw new CustomException(ErrorCode.OAUTH_FAILED);
        }
    }

    // 인가코드 → 소셜 액세스토큰 교환
    private String requestToken(Provider provider, String code) {
        OAuthProperties.Registration config = getConfig(provider);

        String tokenUrl = switch (provider) {
            case KAKAO -> "https://kauth.kakao.com/oauth/token";
            case NAVER -> "https://nid.naver.com/oauth2.0/token";
            case GOOGLE -> "https://oauth2.googleapis.com/token";
            default -> throw new CustomException(ErrorCode.OAUTH_FAILED);
        };

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", config.getClientId());
        params.add("client_secret", config.getClientSecret());
        params.add("redirect_uri", config.getRedirectUri());
        params.add("code", code);
        if (provider == Provider.NAVER) {
            params.add("state", "routick");
        }

        JsonNode response = restClient.post()
                .uri(tokenUrl)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(params)
                .retrieve()
                .body(JsonNode.class);

        return response.get("access_token").asText();
    }

    // 소셜 액세스토큰 → 사용자 정보 조회 (3사 응답 구조가 달라서 각각 파싱)
    private OAuthUserInfo requestUserInfo(Provider provider, String accessToken) {
        String userInfoUrl = switch (provider) {
            case KAKAO -> "https://kapi.kakao.com/v2/user/me";
            case NAVER -> "https://openapi.naver.com/v1/nid/me";
            case GOOGLE -> "https://www.googleapis.com/oauth2/v2/userinfo";
            default -> throw new CustomException(ErrorCode.OAUTH_FAILED);
        };

        JsonNode body = restClient.get()
                .uri(userInfoUrl)
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .body(JsonNode.class);

        return switch (provider) {
            case KAKAO -> {
                JsonNode account = body.path("kakao_account");
                yield new OAuthUserInfo(
                        body.path("id").asText(),
                        account.path("email").asText(null),
                        account.path("profile").path("nickname").asText(null),
                        account.path("profile").path("profile_image_url").asText(null));
            }
            case NAVER -> {
                JsonNode res = body.path("response");
                yield new OAuthUserInfo(
                        res.path("id").asText(),
                        res.path("email").asText(null),
                        res.path("nickname").asText(null),
                        res.path("profile_image").asText(null));
            }
            case GOOGLE -> new OAuthUserInfo(
                    body.path("id").asText(),
                    body.path("email").asText(null),
                    body.path("name").asText(null),
                    body.path("picture").asText(null));
            default -> throw new CustomException(ErrorCode.OAUTH_FAILED);
        };
    }

    private OAuthProperties.Registration getConfig(Provider provider) {
        OAuthProperties.Registration config = properties.getProviders().get(provider.name().toLowerCase());
        if (config == null) throw new CustomException(ErrorCode.OAUTH_FAILED);
        return config;
    }
}