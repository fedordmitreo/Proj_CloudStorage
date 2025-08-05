import psycopg2
import bcrypt

db_params = {
    'dbname': 'storagedata',
    'user': 'postgres',
    'password': '09032011',
    'host': '10.0.0.102',
    'port': '5432'
}


def get_connection():
    return psycopg2.connect(**db_params)


def register_user(name, email, password):
    try:
        # Хеширование пароля
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s);", (name, email, hashed_password))
        connection.commit()
    except Exception as error:
        print("Ошибка при регистрации пользователя:", error)
    finally:
        cursor.close()
        connection.close()


def authenticate_user(email, password):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE email = %s;", (email,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            # Проверка пароля
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return True  # Аутентификация успешна
        return False  # Неверный email или пароль
    except Exception as error:
        print("Ошибка при аутентификации пользователя:", error)
        return None
    finally:
        cursor.close()
        connection.close()
