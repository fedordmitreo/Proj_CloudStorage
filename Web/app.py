from flask import Flask, request, render_template, redirect, url_for, flash, session
from database import register_user, authenticate_user


app = Flask(__name__)
app.secret_key = "testtesttest111"


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
        session['user_id'] = user_id  # Сохраняем ID в сессии, если потребуется
        flash("Регистрация прошла успешно!")
    except Exception as e:
        flash("Ошибка при регистрации: " + str(e))

    return redirect(url_for("home"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    user_name = authenticate_user(email, password)
    if user_name:
        session['user_name'] = user_name
        flash("Вход выполнен успешно!")
        return redirect(url_for("dashboard"))
    else:
        flash("Неверный email или пароль.")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

