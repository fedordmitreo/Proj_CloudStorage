package com.Proj_cloudStorage.bot;

import com.Proj_cloudStorage.Main;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

public class TelegramBots extends TelegramLongPollingBot {
    public String token = "";
    public String chat_id = "";
    public Integer topic_id;
    public String username = "";
    public String password = "";
    public String sender = "";

    public TelegramBots(Main.Config config){
        this.token = config.token;
        this.chat_id = config.chat_id;
        this.topic_id = config.topic_id;
        this.username = config.username;
        this.password = config.password;
        this.sender = config.sender;
    }

    @Override
    public void onUpdateReceived(Update update) {
        String firstWord = "";
        String input = update.getMessage().getText();
        String[] parts = input.split(" ");

        if (parts.length == 0) {
            System.out.println("Пустая строка");
        }
        else {
            firstWord = parts[0];
        }


        switch (firstWord){
            case "/delete_files":

                break;
            case "/db":
                if (parts.length >= 4){
                    String user = parts[1];
                    String pass = parts[2];
                    String email = parts[3];
                    if (parts.length == 5){
                        String admin = parts[4];
                        db.register_user(user, email, pass, admin);
                        sendMessage("Ваши данные были успешно добавлены, слава!");
                    }
                    else{
                        String admin = "ddd";
                        db.register_user(user, email, pass, admin);
                        sendMessage("Ваши данные были успешно добавлены");
                    }

                }
                else{
                    sendMessage("Что то неправильно, перепроверьте сообщение");
                }
                break;
            case "/start":
                sendMessage("Добро пожаловать, господи я заебался");
                break;
        }
    }

    @Override
    public String getBotUsername() {
        return username;
    }

    @Override
    public String getBotToken(){
        return token;
    }

    public void sendMessage(String text){
        SendMessage sendMessage = new SendMessage();
        sendMessage.setChatId(chat_id);
        sendMessage.setMessageThreadId(topic_id);
        sendMessage.setText(text);

        try{
            this.execute(sendMessage);
        } catch (TelegramApiException e){
            throw new RuntimeException(e);
        }
    }
}
