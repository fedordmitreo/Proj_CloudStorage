from flask import Flask, request, render_template, redirect, url_for, flash
from database import register_user, authenticate_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")  # Новый маршрут для dashboard


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    try:
        register_user(name, email, password)
        flash("Регистрация прошла успешно!")
    except Exception as e:
        flash("Ошибка при регистрации: " + str(e))

    return redirect(url_for("home"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # Аутентификация пользователя
    user = authenticate_user(email, password)
    if user:
        flash("Вход выполнен успешно!")
        return redirect(url_for("dashboard"))  # Перенаправление на dashboard при успешном входе
    else:
        flash("Неверный email или пароль.")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
