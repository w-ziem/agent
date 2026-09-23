package agent.platform.common.properties;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "telegram")
public record TelegramProperties(
        @NotBlank String baseUrl,
        @NotBlank String apiToken,
        @NotNull String allowedChatId) {

    public String getBotUrl() {
        return baseUrl + apiToken;
    }

    @Override
    public String toString() {
        return "TelegramProperties{" +
                "baseUrl='" + baseUrl + '\'' +
                ", apiToken='" + apiToken + '\'' +
                ", allowedChatId=" + allowedChatId +
                '}';
    }
}
