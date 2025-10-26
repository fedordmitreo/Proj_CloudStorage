package com.Proj_cloudStorage.bot;

import jakarta.mail.*;
import jakarta.mail.internet.*;

import java.util.*;

public class emailf {
    // Карта SMTP-настроек по домену
    private static final Map<String, SmtpConfig> SMTP_SERVERS = new HashMap<>();

    static {
        SmtpConfig gmail = new SmtpConfig("smtp.gmail.com", 587, true);
        SmtpConfig yandex = new SmtpConfig("smtp.yandex.ru", 587, true);
        SmtpConfig mailRu = new SmtpConfig("smtp.mail.ru", 587, true);
        SmtpConfig outlook = new SmtpConfig("smtp-mail.outlook.com", 587, true);

        SMTP_SERVERS.put("gmail.com", gmail);
        SMTP_SERVERS.put("yandex.ru", yandex);
        SMTP_SERVERS.put("yandex.com", yandex);
        SMTP_SERVERS.put("mail.ru", mailRu);
        SMTP_SERVERS.put("bk.ru", mailRu);
        SMTP_SERVERS.put("list.ru", mailRu);
        SMTP_SERVERS.put("inbox.ru", mailRu);
        SMTP_SERVERS.put("outlook.com", outlook);
        SMTP_SERVERS.put("hotmail.com", outlook);
    }

    // Класс для хранения конфигурации SMTP
    private static class SmtpConfig {
        final String server;
        final int port;
        final boolean tls;

        SmtpConfig(String server, int port, boolean tls) {
            this.server = server;
            this.port = port;
            this.tls = tls;
        }
    }

    /**
     * Определяет SMTP-настройки по email-адресу
     */
    private static SmtpConfig getSmtpConfig(String email) throws IllegalArgumentException {
        String domainPattern = "@([a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})";
        java.util.regex.Pattern pattern = java.util.regex.Pattern.compile(domainPattern);
        java.util.regex.Matcher matcher = pattern.matcher(email.toLowerCase());

        if (!matcher.find()) {
            throw new IllegalArgumentException("Неверный формат email");
        }

        String domain = matcher.group(1);

        // Проверяем, заканчивается ли домен на один из известных
        for (Map.Entry<String, SmtpConfig> entry : SMTP_SERVERS.entrySet()) {
            if (domain.endsWith(entry.getKey())) {
                return entry.getValue();
            }
        }

        throw new IllegalArgumentException("SMTP-сервер для домена '" + domain + "' не поддерживается");
    }

    /**
     * Отправляет письмо.
     *
     * @param to      Адрес получателя
     * @param html    Флаг: использовать ли HTML-формат тела
     * @return true при успешной отправке, иначе false
     */
    public static boolean sendEmail(String to, boolean html, String sender, String password) {
        String subject = "Удаление ваших данных с сайта ВШП";

        String body = """
                Здравствуйте!

                Мы информируем вас о том, что файлы, размещённые вами на нашем сайте, были удалены.
                Причина — использование нецензурной лексики в содержимом загруженных материалов.

                Наш сервис придерживается правил, направленных на поддержание уважительной и безопасной среды для всех пользователей.
                Согласно этим правилам, публикация контента с оскорбительными или ненормативными выражениями запрещена.

                Просим вас учитывать данное требование при дальнейшем использовании платформы.
                Вы можете загрузить обновлённые версии файлов, соответствующие правилам использования.

                Если у вас возникли вопросы, свяжитесь с нами — мы готовы помочь.

                С уважением, Администрация
                """;

        if (sender == null || sender.trim().isEmpty()) {
            System.err.println("❌ Не указан EMAIL_USER");
            return false;
        }
        if (password == null || password.trim().isEmpty()) {
            System.err.println("❌ Не указан EMAIL_PASSWORD");
            return false;
        }

        try {
            SmtpConfig config = getSmtpConfig(sender);
            Properties props = new Properties();
            props.put("mail.smtp.host", config.server);
            props.put("mail.smtp.port", String.valueOf(config.port));
            props.put("mail.smtp.auth", "true");
            props.put("mail.smtp.starttls.enable", String.valueOf(config.tls));

            Session session = Session.getInstance(props, new Authenticator() {
                @Override
                protected PasswordAuthentication getPasswordAuthentication() {
                    return new PasswordAuthentication(sender, password);
                }
            });

            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress(sender));
            message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
            message.setSubject(subject);

            String contentType = html ? "text/html; charset=UTF-8" : "text/plain; charset=UTF-8";
            message.setContent(body, contentType);

            Transport.send(message);

            System.out.printf("✅ Письмо отправлено на %s через %s%n", to, config.server);
            return true;

        } catch (AuthenticationFailedException e) {
            System.err.println("❌ Ошибка аутентификации: неверный логин или пароль");
            return false;
        } catch (SendFailedException e) {
            System.err.println("❌ Ошибка: получатель отклонён");
            return false;
        } catch (Exception e) {
            System.err.println("❌ Ошибка при отправке: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}
