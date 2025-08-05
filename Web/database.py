import psycopg2
import bcrypt
import os

db_params = {
    'dbname': 'storagedata',
    'user': 'postgres',
    'password': '09032011',
    'host': '10.0.0.102',
    'port': '5432'
}

USER_FILES_BASE_DIR = "User_Files"

def get_connection():
    return psycopg2.connect(**db_params)

def register_user(name, email, password):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING user_id;",
            (name, email, hashed_password)
        )

        user_id = cursor.fetchone()[0]
        connection.commit()

        # Создание директории для пользователя
        user_folder_path = os.path.join(USER_FILES_BASE_DIR, str(user_id))
        os.makedirs(user_folder_path, exist_ok=True)
        print(f"Папка для пользователя {user_id} создана: {user_folder_path}")

        return user_id  # Возвращаем ID, если нужно

    except Exception as error:
        print("Ошибка при регистрации пользователя:", error)
        raise error  # чтобы пробросить ошибку обратно в Flask
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def authenticate_user(email, password):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name, password FROM users WHERE email = %s;", (email,))
        result = cursor.fetchone()

        if result:
            name, stored_password = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return name
        return None
    except Exception as error:
        print("Ошибка при аутентификации пользователя:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
