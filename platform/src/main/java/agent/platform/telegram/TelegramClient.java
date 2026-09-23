package agent.platform.telegram;

import agent.platform.common.properties.TelegramProperties;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;


@Component
@RequiredArgsConstructor
@RestController
public class TelegramClient {
    private final TelegramProperties properties;
    private HttpClient httpClient;

    @PostConstruct
    void init() {
        this.httpClient = HttpClient.newHttpClient();
        System.out.println("TelegramProperties: " + properties);
    }

    private HttpRequest buildRequest(String message) throws URISyntaxException {
        URI uriWithQueryParams = UriComponentsBuilder.fromUriString(properties.getBotUrl() + "/sendMessage")
                .queryParam("chat_id", String.valueOf(properties.allowedChatId()))
                .queryParam("text", message)
                .build()
                .toUri();

        System.out.println("builded URI:" + uriWithQueryParams);

        return HttpRequest.newBuilder()
                .uri(uriWithQueryParams)
                .GET()
                .build();
    }


    private void sendMessage(String message) {
        try {
            HttpRequest request = buildRequest(message);
            httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                    .thenAccept(response -> {
                        if (response.statusCode() == 200) {
                            System.out.println("Message sent successfully: " + response.body());
                        } else {
                            System.err.println("Failed to send message. Status code: " + response.statusCode());
                        }
                    })
                    .exceptionally(ex -> {
                        System.err.println("Error sending message: " + ex.getMessage());
                        return null;

                    });
        } catch (URISyntaxException e) {
            System.err.println("Invalid URI syntax: " + e.getMessage());
        }
    }

    @PostMapping("/message")
    public void sendBotMessage(@RequestParam String msg) {
        this.sendMessage(msg);
    }
}
