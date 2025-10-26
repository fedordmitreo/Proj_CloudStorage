package com.Proj_cloudStorage;

import com.Proj_cloudStorage.bot.TelegramBots;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;
import org.yaml.snakeyaml.Yaml;

import java.io.*;
import java.nio.file.Files;
import java.util.Map;

public class Main {
    public static class Config {
        public String token;
        public String chat_id;
        public Integer topic_id;
        public String username;
        public String sender;
        public String password;
    }

    public static void main(String[] args) {
        Yaml yaml = new Yaml();
        Config config = null;

        String[] possiblePaths = {
                "config.yml",
                "config/config.yml",
                System.getProperty("user.home") + "/config.yml"
        };

        for (String path : possiblePaths) {
            File file = new File(path);
            if (file.exists()) {
                try (InputStream inputStream = new FileInputStream(file)) {
                    Map<String, Object> data = yaml.load(inputStream);
                    config = new Config();
                    config.token = (String) data.get("token");
                    config.chat_id = (String) data.get("chat-id");
                    config.topic_id = ((Number) data.get("topic-id")).intValue();
                    config.username = (String) data.get("username");
                    config.sender = (String) data.get("sender");
                    config.password = (String) data.get("password");

                    System.out.println("✅ Конфиг загружен из: " + file.getAbsolutePath());
                    break;
                } catch (Exception e) {
                    System.err.println("❌ Ошибка при чтении конфига из: " + path);
                    e.printStackTrace();
                    return;
                }
            }
        }

        if (config == null) {
            createConfigTemplate();
            return;
        }

        try {
            TelegramBotsApi telegramBotsApi = new TelegramBotsApi(DefaultBotSession.class);
            telegramBotsApi.registerBot(new TelegramBots(config));
            System.out.println("🤖 Бот успешно запущен как @" + config.username);
        } catch (TelegramApiException e) {
            System.err.println("❌ Ошибка при регистрации бота:");
            e.printStackTrace();
        }
    }

    private static void createConfigTemplate() {
        String template = "# config.yml - Настройки Telegram бота\n" +
                "token: \"1234567890:YOUR_BOT_TOKEN_HERE\"\n" +
                "chat-id: \"123456789\"\n" +
                "topic-id: 1\n" +
                "username: \"YourBotUsername\"";
        File configFile = new File("config.yml");
        try {
            Files.write(configFile.toPath(), template.getBytes());
            System.out.println("Файл config.yml не найден. Создан шаблон: config.yml");
            System.out.println("Откройте его, введите свои данные и перезапустите бота.");
        } catch (IOException e) {
            System.err.println("Не удалось создать config.yml: " + e.getMessage());
        }
    }
}