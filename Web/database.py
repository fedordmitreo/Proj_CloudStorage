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
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password, IsAdmin) VALUES (%s, %s, %s, %s) RETURNING user_id;",
        (name, email, hashed_password, False)
    )
    user_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    user_folder_path = os.path.join(USER_FILES_BASE_DIR, str(user_id))
    os.makedirs(user_folder_path, exist_ok=True)

    return user_id


def authenticate_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name, password, IsAdmin FROM users WHERE email = %s;", (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        name, stored_password, is_admin = result
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return name, is_admin
    return None, False


def get_user_id_by_email(email):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return user_id


def get_all_users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, IsAdmin FROM users ORDER BY name;")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users