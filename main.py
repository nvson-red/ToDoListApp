import os

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Task

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect nếu người dùng chưa đăng nhập

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title")
    if title:
        new_task = Task(title=title, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.args.get("username", "")  # Lấy username từ URL nếu có

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)

            # Redirect đến trang được lưu trong 'next' hoặc '/' nếu không có 'next'
            next_page = request.args.get("/")
            return redirect(next_page or url_for("index"))

        flash("Invalid username or password", "danger")
    return render_template("login.html", username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    error_message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Kiểm tra xem username đã tồn tại hay chưa
        if User.query.filter_by(username=username).first():
            error_message = "Username already exists!"
        else:
            # Tạo user mới nếu hợp lệ
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login", username=username))

    return render_template("register.html", error_message=error_message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)