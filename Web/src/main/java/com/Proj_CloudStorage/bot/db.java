package com.Proj_cloudStorage.bot;

import java.sql.*;
import java.util.*;

import org.mindrot.jbcrypt.BCrypt;

public class db {

    private static final String URL = "jdbc:postgresql://10.0.0.200:5432/postgres";
    private static final String USER = "tyr";
    private static final String PASSWORD = "postgresEQW1";

    public static boolean register_user(String name, String email, String password, String admin){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            System.out.println("Подключение к PostgreSQL выполнено.");

            if (Objects.equals(admin, "ddd")){
                String hashed = BCrypt.hashpw(password, BCrypt.gensalt());
                System.out.println("Хеш: " + hashed);

                String insertSQL = "INSERT INTO fer (name, email, password, isadmin) VALUES (?, ?, ?, ?)";
                PreparedStatement pstmt = conn.prepareStatement(insertSQL);

                pstmt.setString(1, name);
                pstmt.setString(2, email);
                pstmt.setString(3, hashed);
                pstmt.setBoolean(4, false);
                pstmt.executeUpdate();
                return true;

            } else if (Objects.equals(admin, "Дебоширики")) {
                String hashed = BCrypt.hashpw(password, BCrypt.gensalt());
                System.out.println("Хеш: " + hashed);

                String insertSQL = "INSERT INTO fer (name, email, password, isadmin) VALUES (?, ?, ?, ?)";
                PreparedStatement pstmt = conn.prepareStatement(insertSQL);

                pstmt.setString(1, name);
                pstmt.setString(2, email);
                pstmt.setString(3, hashed);
                pstmt.setBoolean(4, true);
                pstmt.executeUpdate();
                return true;
            }
            else{
                return false;
            }


        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    public static Map<String, Boolean> authenticate_user(String email, String password){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "SELECT name, password, isadmin FROM users WHERE email = ?;";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);
            pstmt.setString(1, email);
            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            if (rs.next()){
                String hashpassword = rs.getString("password");
                boolean match = BCrypt.checkpw(password, hashpassword);
                if (match){
                    String name = rs.getString("name");
                    boolean admin = rs.getBoolean("isasmin");
                    Map<String, Boolean> f = new HashMap<String, Boolean>();
                    f.put(name, admin);
                    return f;
                }
            }

        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public static String get_user_id_by_email(String email){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "SELECT user_id FROM users WHERE email = ?;";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);
            pstmt.setString(1, email);
            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            if (rs.next()){
                String user_id = rs.getString("user_id");
                return user_id;
            }
        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public static ArrayList<String> get_all_users(){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "SELECT user_id, name, email, isadmin FROM users ORDER BY name;";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);

            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            if (rs.next()){
                String user_id = rs.getString("user_id");
                String name = rs.getString("name");
                String email = rs.getString("email");
                boolean admin = rs.getBoolean("isasmin");
                if (admin){
                    String admin3 = "true";
                    ArrayList<String> f = new ArrayList<>();
                    f.add(user_id);
                    f.add(name);
                    f.add(email);
                    f.add(admin3);
                    return f;
                }
                else{
                    String admin3 = "false";
                    ArrayList<String> f = new ArrayList<>();
                    f.add(user_id);
                    f.add(name);
                    f.add(email);
                    f.add(admin3);
                    return f;
                }

            }
        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
        }
        return null;
    }

    public static boolean user_exists(String user_id){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "SELECT 1 FROM users WHERE user_id = ?";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);
            pstmt.setString(1, user_id);
            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            return rs.next();
        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    public static boolean is_admin(String user_id){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "SELECT isadmin FROM users WHERE user_id = ?";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);
            pstmt.setString(1, user_id);
            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            return rs.next();

        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    public static boolean delete_user_from_db(String user_id){
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            String insertSQL = "DELETE FROM users WHERE user_id = ?;";
            PreparedStatement pstmt = conn.prepareStatement(insertSQL);
            pstmt.setString(1, user_id);
            pstmt.executeUpdate();

            ResultSet rs = pstmt.executeQuery();

            return rs.next();

        } catch (SQLException e) {
            System.err.println("Ошибка при работе с PostgreSQL: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}
