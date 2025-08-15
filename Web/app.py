from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import psycopg2
from database import register_user, authenticate_user, get_user_id_by_email, get_all_users
import time

app = Flask(__name__)
app.secret_key = "testtesttest111"

UPLOAD_FOLDER = 'User_Files'
TRASH_FOLDER = 'Trash'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

db_params = {
    'dbname': 'storagedata',
    'user': 'postgres',
    'password': '09032011',
    'host': '10.0.0.102',
    'port': '5432'
}


def create_user_directories(user_id):
    try:
        user_upload = os.path.join(UPLOAD_FOLDER, str(user_id))
        user_trash = os.path.join(TRASH_FOLDER, str(user_id))
        os.makedirs(user_upload, exist_ok=True)
        os.makedirs(user_trash, exist_ok=True)
    except Exception as e:
        print(f"Ошибка при создании папок для пользователя {user_id}: {e}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    try:
        user_id = register_user(name, email, password)
        session['user_id'] = user_id
        session['user_name'] = name
        create_user_directories(user_id)
        flash("Registration was successful!")
    except Exception as e:
        flash("Error: " + str(e))
    return redirect(url_for("home"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    result = authenticate_user(email, password)
    if result and result[0]:
        name, is_admin = result
        user_id = get_user_id_by_email(email)
        session['user_name'] = name
        session['user_id'] = user_id
        create_user_directories(user_id)

        if is_admin:
            return redirect(url_for("admin_panel"))
        else:
            return redirect(url_for("dashboard"))
    else:
        flash("Incorrect email or password.")
        return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Please log in.")
        return redirect(url_for("home"))

    user_id = session['user_id']
    create_user_directories(user_id)

    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if not result:
            flash("User not found.")
            session.clear()
            return redirect(url_for("home"))

        if result[0]:
            return redirect(url_for("admin_panel"))

    except Exception as e:
        print(f"Error in /dashboard: {e}")
        flash("Temporary error.")
        return redirect(url_for("home"))

    user_name = session.get('user_name', 'Пользователь')
    return render_template("dashboard.html", user_name=user_name)


@app.route("/admin")
def admin_panel():
    if 'user_id' not in session:
        flash("Please log in.")
        return redirect(url_for("home"))

    user_id = session['user_id']

    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if not result or not result[0]:
            flash("Access denied.")
            return redirect(url_for("dashboard"))

        users = get_all_users()
        admin_name = session.get('user_name', 'Админ')
        return render_template("admin_panel.html", admin_name=admin_name, users=users)

    except Exception as e:
        print(f"Error in /admin: {e}")
        flash("Failed to load admin panel.")
        return redirect(url_for("dashboard"))



@app.route("/upload", methods=["POST"])
def upload():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Требуется авторизация"}), 401

    user_id = session['user_id']
    create_user_directories(user_id)

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "Файл не выбран"}), 400

    try:
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        file.save(os.path.join(user_folder, filename))
        return jsonify({"success": True, "message": "Файл успешно загружен"}), 200
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"success": False, "message": "Ошибка сохранения"}), 500


@app.route("/files")
def list_files():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    if not os.path.exists(user_folder):
        return jsonify([])
    try:
        files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
        return jsonify(files)
    except Exception as e:
        print(f"Error listing files: {e}")
        return jsonify([])


@app.route("/delete_file", methods=["POST"])
def delete_file():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False), 401

    filename = request.json.get("filename")
    if not filename:
        return jsonify(success=False), 400

    source_path = os.path.join(UPLOAD_FOLDER, str(user_id), filename)
    trash_dir = os.path.join(TRASH_FOLDER, str(user_id))
    target_path = os.path.join(trash_dir, filename)

    os.makedirs(trash_dir, exist_ok=True)

    try:
        if not os.path.exists(source_path):
            print(f"[INFO] Файл уже удалён или не существует: {source_path}")
            return jsonify(success=True)

        if os.path.exists(target_path):
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            target_path = os.path.join(trash_dir, f"{name}_{timestamp}{ext}")

        os.rename(source_path, target_path)
        print(f"[OK] Файл перемещён в корзину: {filename}")
        return jsonify(success=True)

    except Exception as e:
        print(f"[ERROR] При удалении в корзину: {e}")
        return jsonify(success=True)


@app.route("/trash")
def list_trash():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])
    trash_dir = os.path.join(TRASH_FOLDER, str(user_id))
    if not os.path.exists(trash_dir):
        return jsonify([])
    try:
        files = [f for f in os.listdir(trash_dir) if os.path.isfile(os.path.join(trash_dir, f))]
        return jsonify(files)
    except Exception as e:
        print(f"Error listing trash: {e}")
        return jsonify([])


@app.route("/restore_file", methods=["POST"])
def restore_file():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False), 401

    filename = request.json.get("filename")
    if not filename:
        return jsonify(success=False), 400

    source_path = os.path.join(TRASH_FOLDER, str(user_id), filename)
    dest_path = os.path.join(UPLOAD_FOLDER, str(user_id), filename)

    try:
        if not os.path.exists(source_path):
            print(f"[INFO] Файл в корзине не найден: {source_path}")
            return jsonify(success=True)

        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            dest_path = os.path.join(UPLOAD_FOLDER, str(user_id), f"{name}_{timestamp}{ext}")

        os.rename(source_path, dest_path)
        print(f"[OK] Файл восстановлен: {filename}")
        return jsonify(success=True)

    except Exception as e:
        print(f"[ERROR] При восстановлении: {e}")
        return jsonify(success=True)


@app.route("/delete_permanently", methods=["POST"])
def delete_permanently():
    user_id = session.get("user_id")
    if not user_id:
        print("[DELETE PERM] Пользователь не авторизован")
        return jsonify(success=True)

    filename = request.json.get("filename")
    if not filename:
        print("[DELETE PERM] Имя файла не указано")
        return jsonify(success=True)

    file_path = os.path.join(TRASH_FOLDER, str(user_id), filename)
    print(f"[DELETE PERM] Путь к файлу: {file_path}")

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[OK] Файл удалён: {file_path}")
        else:
            print(f"[WARNING] Файл не найден (уже удалён): {file_path}")
        return jsonify(success=True)
    except Exception as e:
        print(f"[ERROR] Не удалось удалить файл: {e}")
        return jsonify(success=True)


@app.route("/download/<filename>")
def download_file(filename):
    user_id = session.get("user_id")
    if not user_id:
        flash("You are not logged in.")
        return redirect(url_for("home"))

    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        return send_from_directory(user_folder, filename, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for("dashboard"))


import shutil

@app.route("/admin/clear_user_files/<int:user_id>", methods=["POST"])
def clear_user_files(user_id):
    if 'user_id' not in session:
        return jsonify({"success": False}), 401

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (session['user_id'],))
        is_admin = cur.fetchone()
        cur.close()
        conn.close()

        if not is_admin or not is_admin[0]:
            return jsonify({"success": False}), 403

        user_upload = os.path.join(UPLOAD_FOLDER, str(user_id))
        user_trash = os.path.join(TRASH_FOLDER, str(user_id))

        if os.path.exists(user_upload):
            shutil.rmtree(user_upload)
        if os.path.exists(user_trash):
            shutil.rmtree(user_trash)

        os.makedirs(user_upload, exist_ok=True)
        os.makedirs(user_trash, exist_ok=True)

        return jsonify({"success": True, "message": "Файлы очищены"})

    except Exception as e:
        print(f"[ADMIN ERROR] clear_user_files: {e}")
        return jsonify({"success": False}), 500


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({"success": False}), 401

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (session['user_id'],))
        is_admin = cur.fetchone()

        if not is_admin or not is_admin[0]:
            cur.close()
            conn.close()
            return jsonify({"success": False}), 403

        cur.execute("SELECT user_id FROM users WHERE user_id = %s;", (user_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False}), 404

        cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
        conn.commit()
        cur.close()
        conn.close()

        user_upload = os.path.join(UPLOAD_FOLDER, str(user_id))
        user_trash = os.path.join(TRASH_FOLDER, str(user_id))

        if os.path.exists(user_upload):
            shutil.rmtree(user_upload)
        if os.path.exists(user_trash):
            shutil.rmtree(user_trash)

        return jsonify({"success": True, "message": "Пользователь удалён"})

    except Exception as e:
        print(f"[ADMIN ERROR] delete_user: {e}")
        return jsonify({"success": False}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)