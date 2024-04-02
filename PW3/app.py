import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Shepel_123'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.date_of_birth}')"


@app.route("/user")
def user():
    username = session.get("username")
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("user.html", username=user.username, email=user.email, date_of_birth=user.date_of_birth)
    # Якщо користувач не залогінений або його дані не знайдено, можна перенаправити його на сторінку входу або вивести повідомлення про помилку
    return redirect(url_for("login"))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Отримання даних з форми входу
        username = request.form["username"]
        password = request.form["password"]
        # Перевірка користувача в базі даних (необхідно самостійно реалізувати)
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Якщо користувач існує, встановлюємо сесію та перенаправляємо на сторінку користувача
            session["username"] = user.username
            return redirect(url_for("user"))
        else:
            # Якщо користувач не існує, виводимо повідомлення про помилку
            return "Invalid username or password"
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Отримання даних з форми реєстрації
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        date_of_birth = request.form["date_of_birth"]

        # Перевірка, чи паролі співпадають
        if password != confirm_password:
            return "Passwords do not match"

        # Перевірка унікальності логіну та email
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            return "Username already exists, please choose another one"
        elif existing_email:
            return "Email already exists, please use another one"
        elif len(password) < 8:
            return "Password should be at least 8 characters long"
        else:
            # Перетворення рядка дати народження у об'єкт datetime
            try:
                dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD format for the date of birth."

            # Створення нового користувача у базі даних
            new_user = User(username=username, email=email, date_of_birth=dob, password=password)
            db.session.add(new_user)
            db.session.commit()

            # Перенаправлення на сторінку входу після успішної реєстрації
            return redirect(url_for("login"))
    else:
        return render_template("registration.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        # Очищення сесії
        session.clear()
        # Перенаправлення на головну сторінку (або на сторінку входу)
        return redirect(url_for("login"))
    else:
        # Опціонально: додатковий код для GET-запитів на /logout
        return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)

