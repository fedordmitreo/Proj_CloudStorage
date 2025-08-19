import psycopg2
import bcrypt

def get_connection():
    return psycopg2.connect(
        dbname='storagedata',
        user='postgres',
        password='09032011',
        host='10.0.0.102',
        port='5432'
    )

def register_user(name, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, password, IsAdmin) VALUES (%s, %s, %s, %s) RETURNING user_id;",
                    (name, email, hashed_password, False)
                )
                user_id = cur.fetchone()[0]
        return user_id
    except psycopg2.IntegrityError:
        raise Exception("Email уже зарегистрирован")
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, password, IsAdmin FROM users WHERE email = %s;", (email,))
                result = cur.fetchone()
        if result:
            name, stored_password, is_admin = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return name, is_admin
        return None, False
    finally:
        conn.close()

def get_user_id_by_email(email):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
                row = cur.fetchone()
                return row[0] if row else None
    finally:
        conn.close()

def get_all_users():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, name, email, IsAdmin FROM users ORDER BY name;")
                return cur.fetchall()
    finally:
        conn.close()

def user_exists(user_id):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE user_id = %s;", (user_id,))
                return cur.fetchone() is not None
    finally:
        conn.close()

def is_admin(user_id):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (user_id,))
                row = cur.fetchone()
                return row[0] if row else False
    finally:
        conn.close()

def delete_user_from_db(user_id):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
    finally:
        conn.close()
