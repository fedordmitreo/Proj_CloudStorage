import psycopg2
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from database import register_user, authenticate_user, get_user_id_by_email, get_all_users

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

import shutil

@app.route("/admin/clear_user_files/<int:user_id>", methods=["POST"])
def clear_user_files(user_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Требуется вход"}), 401

    # Проверяем, что текущий пользователь — админ
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (session['user_id'],))
    is_admin = cursor.fetchone()
    cursor.close()
    connection.close()

    if not is_admin or not is_admin[0]:
        return jsonify({"success": False, "message": "Доступ запрещён"}), 403

    # Удаляем файлы пользователя
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    trash_folder = os.path.join(TRASH_FOLDER, str(user_id))

    try:
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)  # Удаляем папку с файлами
        if os.path.exists(trash_folder):
            shutil.rmtree(trash_folder)  # Удаляем корзину

        return jsonify({"success": True, "message": "Файлы пользователя удалены"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка при удалении файлов: {str(e)}"}), 500


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Требуется вход"}), 401

    # Проверяем, что текущий пользователь — админ
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (session['user_id'],))
    is_admin = cursor.fetchone()
    if not is_admin or not is_admin[0]:
        cursor.close()
        return jsonify({"success": False, "message": "Доступ запрещён"}), 403

    # Получаем email для удаления папки (если нужно)
    cursor.execute("SELECT email FROM users WHERE user_id = %s;", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        return jsonify({"success": False, "message": "Пользователь не найден"}), 404

    # Удаляем файлы
    user_files = os.path.join(UPLOAD_FOLDER, str(user_id))
    user_trash = os.path.join(TRASH_FOLDER, str(user_id))

    try:
        if os.path.exists(user_files):
            shutil.rmtree(user_files)
        if os.path.exists(user_trash):
            shutil.rmtree(user_trash)

        # Удаляем из базы
        cursor.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Пользователь и его файлы удалены"})
    except Exception as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({"success": False, "message": f"Ошибка при удалении: {str(e)}"}), 500

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
        session['user_name'] = name
        session['user_id'] = get_user_id_by_email(email)

        # Редирект в зависимости от роли
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

    # Если пользователь — админ, но зашёл на /dashboard — перенаправляем
    email = request.args.get('email') or session.get('user_name')
    user_id = session.get('user_id')
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (user_id,))
    is_admin = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    if is_admin:
        return redirect(url_for("admin_panel"))

    user_name = session.get('user_name', 'Пользователь')
    return render_template("dashboard.html", user_name=user_name)


@app.route("/admin")
def admin_panel():
    if 'user_id' not in session:
        flash("Please log in.")
        return redirect(url_for("home"))

    user_id = session['user_id']

    # Проверяем, админ ли
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute("SELECT IsAdmin FROM users WHERE user_id = %s;", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if not result or not result[0]:
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    users = get_all_users()  # Получаем всех пользователей
    admin_name = session.get('user_name', 'Админ')
    return render_template("admin_panel.html", admin_name=admin_name, users=users)


# --- Файловые маршруты (остаются без изменений) ---

@app.route("/upload", methods=["POST"])
def upload():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Требуется авторизация"}), 401

    user_id = session['user_id']
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "message": "Файл не выбран"}), 400

    filename = secure_filename(file.filename)
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    file.save(os.path.join(user_folder, filename))

    return jsonify({"success": True, "message": "Файл успешно загружен"}), 200


@app.route("/files")
def list_files():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    files = os.listdir(user_folder)
    return jsonify(files)


@app.route("/delete_file", methods=["POST"])
def delete_file():
    user_id = session.get("user_id")
    filename = request.json.get("filename")
    source_path = os.path.join(UPLOAD_FOLDER, str(user_id), filename)
    trash_path = os.path.join(TRASH_FOLDER, str(user_id))
    os.makedirs(trash_path, exist_ok=True)
    os.rename(source_path, os.path.join(trash_path, filename))
    return jsonify(success=True)


@app.route("/trash")
def list_trash():
    user_id = session.get("user_id")
    trash_path = os.path.join(TRASH_FOLDER, str(user_id))
    if not os.path.exists(trash_path):
        return jsonify([])
    return jsonify(os.listdir(trash_path))


@app.route("/restore_file", methods=["POST"])
def restore_file():
    user_id = session.get("user_id")
    filename = request.json.get("filename")
    trash_path = os.path.join(TRASH_FOLDER, str(user_id), filename)
    restore_path = os.path.join(UPLOAD_FOLDER, str(user_id), filename)
    os.rename(trash_path, restore_path)
    return jsonify(success=True)


@app.route("/delete_permanently", methods=["POST"])
def delete_permanently():
    user_id = session.get("user_id")
    filename = request.json.get("filename")
    file_path = os.path.join(TRASH_FOLDER, str(user_id), filename)
    os.remove(file_path)
    return jsonify(success=True)


@app.route("/download/<filename>")
def download_file(filename):
    user_id = session.get("user_id")
    if not user_id:
        flash("You are not logged in.")
        return redirect(url_for("home"))

    user_folder = os.path.join("User_Files", str(user_id))
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        return send_from_directory(user_folder, filename, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)