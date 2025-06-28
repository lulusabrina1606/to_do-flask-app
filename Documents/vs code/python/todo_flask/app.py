from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "secret-key"  # Ganti dengan secret key kamu sendiri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Model database
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Relasi ke user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username sudah dipakai!")
            return redirect(url_for("register"))
        new_user = User(username=username, password=password)  # NOTE: password sebaiknya di-hash
        db.session.add(new_user)
        db.session.commit()
        flash("Registrasi berhasil, silakan login!")
        return redirect(url_for("login"))
    return render_template("register.html")

# Buat database kalau belum ada
with app.app_context():
    db.create_all()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Username atau password salah!")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Berhasil logout!")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", todos=todos)

@app.route("/add", methods=["POST"])
@login_required
def add():
    task_text = request.form.get("task")
    if task_text:
        new_task = Todo(task=task_text, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/toggle/<int:id>")
def toggle(id):
    task = Todo.query.get_or_404(id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5050)
