from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-chosen'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        entered_email = request.form.get("email")
        user_email = User.query.filter_by(email=entered_email).first()
        if user_email:
            return render_template("login.html", error="Email Id already registered")
        else:
            new_user = User(
                email=request.form.get("email"),
                name=request.form.get("name"),
                password=generate_password_hash(request.form.get("password"), method="pbkdf2:sha256", salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            load_user(new_user)
            return render_template("secrets.html", name=new_user.name)
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_email = request.form.get("email")
        entered_password = request.form.get("password")
        user = User.query.filter_by(email=entered_email).first()
        if check_password_hash(user.password, entered_password):
            load_user(user.id)
            return render_template("secrets.html", name=user.name)
        else:
            return render_template("login.html", error="Invalid Username/Password")
    else:
        return render_template("login.html")


@app.route('/secrets/<name>')
def secrets(name):
    return render_template("secrets.html", name=name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory('static', filename="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
