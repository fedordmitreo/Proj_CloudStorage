import psycopg2
import bcrypt

# Параметры подключения к базе данных
db_params = {
    'dbname': 'storagedata',
    'user': 'postgres',
    'password': '09032011',
    'host': '10.0.0.102',
    'port': '5432'
}

# Получение подключения к базе
def get_connection():
    return psycopg2.connect(**db_params)

# Регистрация пользователя
def register_user(name, email, password):
    try:
        # Хеширование пароля и преобразование в строку
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s);",
            (name, email, hashed_password)
        )
        connection.commit()
        print("Пользователь успешно зарегистрирован.")
    except Exception as error:
        print("Ошибка при регистрации пользователя:", error)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# Аутентификация пользователя
def authenticate_user(email, password):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE email = %s;", (email,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]  # Ожидаем строку
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                print("Аутентификация успешна.")
                return True
            else:
                print("Неверный пароль.")
        else:
            print("Пользователь с таким email не найден.")
        return False
    except Exception as error:
        print("Ошибка при аутентификации пользователя:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
