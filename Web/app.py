from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from database import register_user, authenticate_user, get_user_id_by_email

app = Flask(__name__)
app.secret_key = "testtesttest111"

UPLOAD_FOLDER = 'User_Files'
TRASH_FOLDER = 'Trash'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user_name = session.get('user_name', 'Пользователь')
    return render_template("dashboard.html", user_name=user_name)

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
    user_name = authenticate_user(email, password)
    if user_name:
        session['user_name'] = user_name
        session['user_id'] = get_user_id_by_email(email)
        flash("Login successful!")
        return redirect(url_for("dashboard"))
    else:
        flash("Incorrect email or password.")
        return redirect(url_for("home"))

@app.route("/upload", methods=["POST"])
def upload():
    if 'user_id' not in session:
        flash("Authorization required.")
        return redirect(url_for("home"))

    user_id = session['user_id']
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        file.save(os.path.join(user_folder, filename))
        flash("File uploaded successfully.")
    return redirect(url_for("dashboard"))

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
    app.run(debug=False, host="0.0.0.0", port='5000')