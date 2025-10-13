from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory
import os
import logging
import time
import shutil
from bot import log
from database import (
    register_user,
    authenticate_user,
    get_user_id_by_email,
    get_all_users,
    user_exists,
    is_admin,
    delete_user_from_db
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
g = 555

app = Flask(__name__)
app.secret_key = g

UPLOAD_FOLDER = 'User_Files'
TRASH_FOLDER = 'Trash'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRASH_FOLDER'] = TRASH_FOLDER

def create_user_directories(user_id):
    try:
        user_upload = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
        user_trash = os.path.join(app.config['TRASH_FOLDER'], str(user_id))
        os.makedirs(user_upload, exist_ok=True)
        os.makedirs(user_trash, exist_ok=True)
    except Exception as e:
        logger.error(f"Ошибка при создании папок для пользователя {user_id}: {e}")
        log(f"Ошибка при создании папок для пользователя {user_id}: {e}")


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    if not user_exists(user_id):
        return None
    name = session.get('user_name', 'Пользователь')
    admin_status = is_admin(user_id)
    return {'id': user_id, 'name': name, 'is_admin': admin_status}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_id = register_user(name, email, password)
        session['user_id'] = user_id
        session['user_name'] = name
        create_user_directories(user_id)
        flash("Регистрация прошла успешно!", "success")
        log(f"Регистрация прошла успешно! {name} {user_id}")
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Ошибка регистрации: {str(e)}", "error")
        log(f"Ошибка регистрации: {str(e)}")
        return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    try:
        email = request.form["email"]
        password = request.form["password"]
        result = authenticate_user(email, password)
        if result and result[0]:
            name, is_admin_flag = result
            user_id = get_user_id_by_email(email)
            if user_id is None:
                flash("Ошибка: пользователь не найден.", "error")
                log(f"Ошибка: пользователь не найден. {email}")
                return redirect(url_for("home"))

            session['user_name'] = name
            session['user_id'] = user_id
            create_user_directories(user_id)
            return redirect(url_for("admin_panel")) if is_admin_flag else redirect(url_for("dashboard"))
        else:
            flash("Неверный email или пароль.", "error")
            log(f"Неверный email или пароль. {session['user_id']}")
            return redirect(url_for("home"))
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
        flash("Произошла ошибка на сервере. Попробуйте позже.", "error")
        log(f"Ошибка при входе: {e}")
        return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for("home"))

    if user['is_admin']:
        return redirect(url_for("admin_panel"))

    return render_template("dashboard.html", user_name=user['name'])

@app.route("/admin")
def admin_panel():
    user = get_current_user()
    if not user:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for("home"))
    if not user['is_admin']:
        flash("Доступ запрещён.", "error")
        return redirect(url_for("dashboard"))

    users = get_all_users()
    return render_template("admin_panel.html", admin_name=user['name'], users=users)

@app.route("/upload", methods=["POST"])
def upload():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Требуется авторизация"}), 401

    user_id = session['user_id']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    create_user_directories(user_id)  # убедитесь, что эта функция не мешает

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "Файл не выбран"}), 400

    try:
        filename = file.filename
        filepath = os.path.join(user_folder, filename)

        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}{ext}"
            filepath = os.path.join(user_folder, filename)

        logger.debug(f"Загружаемый файл: {filename}")
        file.save(filepath)
        logger.info(f"Файл успешно сохранен: {filename}")
        log(f"Файл сохранён {user_id} {filename}")
        return jsonify({"success": True, "message": "Файл успешно загружен"}), 200
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {e}")
        log(f"Файл ошибка {user_id} {file.filename}")
        return jsonify({"success": False, "message": "Ошибка сохранения"}), 500

@app.route("/files")
def list_files():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    if not os.path.exists(user_folder):
        return jsonify([])
    try:
        files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
        return jsonify(files)
    except Exception as e:
        logger.error(f"Ошибка чтения файлов: {e}")
        log(f"Ошибка чтения файлов: {e} {user_id}")
        return jsonify([])

@app.route("/delete_file", methods=["POST"])
def delete_file():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False), 401

    filename = request.json.get("filename")
    if not filename:
        return jsonify(success=False), 400

    source_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), filename)
    trash_dir = os.path.join(app.config['TRASH_FOLDER'], str(user_id))
    target_path = os.path.join(trash_dir, filename)

    os.makedirs(trash_dir, exist_ok=True)

    try:
        if not os.path.exists(source_path):
            return jsonify(success=True)

        if os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            target_path = os.path.join(trash_dir, f"{name}_{timestamp}{ext}")

        os.rename(source_path, target_path)
        logger.info(f"Файл в корзину: {filename}")
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        log(f"Ошибка удаления: {e} {user_id} {filename}")
        return jsonify(success=False), 500

@app.route("/trash")
def list_trash():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])
    trash_dir = os.path.join(app.config['TRASH_FOLDER'], str(user_id))
    if not os.path.exists(trash_dir):
        return jsonify([])
    try:
        files = [f for f in os.listdir(trash_dir) if os.path.isfile(os.path.join(trash_dir, f))]
        return jsonify(files)
    except Exception as e:
        logger.error(f"Ошибка корзины: {e}")
        log(f"Ошибка корзины: {e} {user_id}")
        return jsonify([])

@app.route("/restore_file", methods=["POST"])
def restore_file():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False), 401

    filename = request.json.get("filename")
    if not filename:
        return jsonify(success=False), 400

    source_path = os.path.join(app.config['TRASH_FOLDER'], str(user_id), filename)
    dest_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), filename)

    try:
        if not os.path.exists(source_path):
            return jsonify(success=True)

        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), f"{name}_{timestamp}{ext}")

        os.rename(source_path, dest_path)
        logger.info(f"Файл восстановлен: {filename}")
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"Ошибка восстановления: {e}")
        log(f"Ошибка восстановления: {e} {user_id} {filename}")
        return jsonify(success=False), 500

@app.route("/delete_permanently", methods=["POST"])
def delete_permanently():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False), 401

    filename = request.json.get("filename")
    if not filename:
        return jsonify(success=False), 400

    file_path = os.path.join(app.config['TRASH_FOLDER'], str(user_id), filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл удалён: {filename}")
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        log(f"Ошибка удаления: {e} {user_id} {filename}")
        return jsonify(success=False), 500

@app.route("/download/<filename>")
def download_file(filename):
    if 'user_id' not in session:
        flash("Вы не авторизованы.", "error")
        return redirect(url_for("home"))

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        return send_from_directory(user_folder, filename, as_attachment=True)
    else:
        flash("Файл не найден.", "error")
        log(f"Файл не найден {session['user_id']} {filename}")
        return redirect(url_for("dashboard"))


@app.route("/admin/clear_user_files/<int:user_id>", methods=["POST"])
def clear_user_files(user_id):
    current_user = get_current_user()
    if not current_user or not current_user['is_admin']:
        return jsonify({"success": False}), 403

    user_upload = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    user_trash = os.path.join(app.config['TRASH_FOLDER'], str(user_id))

    try:
        if os.path.exists(user_upload):
            shutil.rmtree(user_upload)
        if os.path.exists(user_trash):
            shutil.rmtree(user_trash)
        os.makedirs(user_upload, exist_ok=True)
        os.makedirs(user_trash, exist_ok=True)
        return jsonify({"success": True, "message": "Файлы очищены"})
    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        log(f"Ошибка очистки админ: {e} {user_id}")
        return jsonify({"success": False}), 500

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    current_user = get_current_user()
    if not current_user or not current_user['is_admin']:
        return jsonify({"success": False}), 403

    if not user_exists(user_id):
        return jsonify({"success": False}), 404

    try:
        delete_user_from_db(user_id)

        user_upload = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
        user_trash = os.path.join(app.config['TRASH_FOLDER'], str(user_id))
        if os.path.exists(user_upload):
            shutil.rmtree(user_upload)
        if os.path.exists(user_trash):
            shutil.rmtree(user_trash)

        return jsonify({"success": True, "message": "Пользователь удалён"})
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        log(f"Ошибка удаления: {e}")
        return jsonify({"success": False}), 500

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TRASH_FOLDER'], exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
