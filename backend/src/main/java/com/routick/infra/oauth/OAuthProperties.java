package com.routick.infra.oauth;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

// oauth.providers.* 설정 바인딩
@Getter
@Setter
@Component
@ConfigurationProperties(prefix = "oauth")
public class OAuthProperties {

    private Map<String, Registration> providers = new HashMap<>();

    @Getter
    @Setter
    public static class Registration {
        private String clientId;
        private String clientSecret;
        private String redirectUri;
    }
}