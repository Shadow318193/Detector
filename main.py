from flask import Flask, request, render_template, redirect, abort, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.user import User
from data.site import Site
from data.request import Request
from data.requesttype import RequestType

import datetime

import os

AVATAR_TYPES = ["png", "jpg", "jpeg", "gif"]
MEDIA_PIC_TYPES = ["png", "jpg", "jpeg", "gif"]
MEDIA_VID_TYPES = ["webm", "mp4"]
MEDIA_AUD_TYPES = ["mp3", "wav"]
MEDIA_TYPES = MEDIA_VID_TYPES + MEDIA_PIC_TYPES + MEDIA_AUD_TYPES


def make_accept_for_html(mime: str):
    # For input tag in HTML
    if mime in MEDIA_PIC_TYPES:
        return "image/" + mime
    elif mime in MEDIA_VID_TYPES:
        return "video/" + mime
    elif mime in MEDIA_AUD_TYPES:
        return "audio/" + mime


def make_readble_time(t: datetime.datetime):
    # Time format: dd.MM.yyyy hh:mm
    new_t = str(t).split()
    new_t[0] = new_t[0].split("-")[::-1]
    new_t[0] = ".".join(new_t[0])
    new_t[1] = new_t[1].split(".")[0]
    new_t = " ".join(new_t)
    return new_t


accept_avatars = ",".join([make_accept_for_html(x) for x in AVATAR_TYPES])
accept_media = ",".join([make_accept_for_html(x) for x in MEDIA_TYPES])


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Cмотреть данную страницу/делать данное действие можно " \
                              "только авторизованным пользователям"


@login_manager.user_loader
def load_user(user_id: int):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


def name_is_correct(name_s: str):
    if not name_s:
        return False
    if not name_s.split() or len(name_s) > 32:
        return False
    return True


def login_is_correct(login_s: str):
    if not login_s:
        return False
    if not login_s.split() or len(login_s) > 32:
        return False
    for i in login_s.lower():
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_":
            return False
    return True


def password_is_correct(password: str):
    if password.islower() or password.isupper() or len(password) < 8:
        return False
    for i in password.lower():
        if i not in "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789!@$#_":
            return False
    digits = ""
    special = ""
    for i in "0123456789":
        if i in password:
            digits += i
    for i in "!@$#":
        if i in password:
            special += i
    if not special or not digits:
        return False
    return True


def update_user_auth_time():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.id == User.id).first()
        user.last_auth = datetime.datetime.now()
        db_sess.commit()


def allowed_type(filename, types):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in types


app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/from_users'
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024


@app.route("/", methods=["GET"])
def index():
    update_user_auth_time()
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template("index.html", current_user=current_user, user=user)
    return redirect("/login")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    update_user_auth_time()
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect("/user/" + current_user.login)
        return render_template("signup.html")
    elif request.method == "POST":
        if not name_is_correct(request.form["name"]):
            flash("Ошибка регистрации: имя не удовлетворяет требованию", "danger")
            return redirect("/signup")
        elif not name_is_correct(request.form["surname"]):
            flash("Ошибка регистрации: фамилия не удовлетворяет требованию", "danger")
            return redirect("/signup")
        elif not login_is_correct(request.form["login"]):
            flash("Ошибка регистрации: логин не удовлетворяет требованию", "danger")
            return redirect("/signup")
        elif len(request.form["email"]) > 64:
            flash("Ошибка регистрации: электронная почта не удовлетворяет требованию", "danger")
            return redirect("/signup")
        if request.form["password"] == request.form["password_sec"] and password_is_correct(request.form["password"]):
            db_sess = db_session.create_session()
            existing_user = db_sess.query(User).filter(User.login == request.form["login"]).first()
            if existing_user:
                flash("Ошибка регистрации: кто-то уже есть с таким логином", "danger")
                return redirect("/signup")
            existing_user = db_sess.query(User).filter(User.email == request.form["email"]).first()
            if existing_user:
                flash("Ошибка регистрации: кто-то уже есть с такой почтой", "danger")
                return redirect("/signup")
            user = User()
            user.name = request.form["name"]
            user.surname = request.form["surname"]
            user.email = request.form["email"]
            user.login = request.form["login"]
            user.hashed_password = generate_password_hash(request.form["password"])
            db_sess.add(user)
            db_sess.commit()
            login_user(user)
            user.last_auth = datetime.datetime.now()
            flash("Регистрация прошла успешно!", "success")
            return redirect("/")
        elif password_is_correct(request.form["password"]):
            flash("Ошибка регистрации: пароль не повторён", "danger")
            return redirect("/signup")
        else:
            flash("Ошибка регистрации: пароль не удовлетворяет требованию", "danger")
            return redirect("/signup")


@app.route("/login", methods=["POST", "GET"])
def login():
    update_user_auth_time()
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect("/")
        return render_template("login.html")
    elif request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.login == request.form["login"])
                                          | (User.email == request.form["login"])).first()
        if user and check_password_hash(user.hashed_password, request.form["password"]):
            login_user(user)
            user.last_auth = datetime.datetime.now()
            flash("Успешный вход", "success")
            return redirect("/")
        elif not user:
            flash("Ошибка входа: неверный логин", "danger")
            return redirect("/login")
        elif not check_password_hash(user.hashed_password, request.form["password"]):
            flash("Ошибка входа: неверный пароль", "danger")
            return redirect("/login")


@app.route("/logout")
@login_required
def logout():
    update_user_auth_time()
    logout_user()
    return redirect("/")


@app.route("/add_site", methods=["POST", "GET"])
def add_site_page():
    update_user_auth_time()
    return render_template("add_site.html")


@app.route("/site_repost", methods=["POST", "GET"])
def site_repost_page():
    update_user_auth_time()
    return render_template("site_repost.html")


@app.route("/popular", methods=["POST", "GET"])
def popular_page():
    update_user_auth_time()
    return render_template("popular.html")


@app.route("/admin", methods=["POST", "GET"])
def admin_page():
    update_user_auth_time()
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template("popular.html")
        else:
            abort(403)
    else:
        abort(401)


@app.errorhandler(401)
def e401(code):
    update_user_auth_time()
    print(code)
    flash("[Ошибка 401] " + login_manager.login_message, "warning")
    return redirect("/")


@app.errorhandler(403)
def e403(code):
    update_user_auth_time()
    print(code)
    flash("[Ошибка 403] Cмотреть данную страницу/делать данное действие можно только администраторам", "warning")
    return redirect("/")


@app.errorhandler(404)
def e404(code):
    update_user_auth_time()
    print(code)
    return render_template("error.html", current_user=current_user, link=request.args.get("from"),
                           code=404, err="Мы не можем показать эту страницу: её не существует")


@app.errorhandler(500)
def e500(code):
    update_user_auth_time()
    print(code)
    return render_template("error.html", current_user=current_user, code=500,
                           err="Извините за неудобство. Сейчас мы активно работаем над причиной проблемы и"
                           " исправляем её")


if __name__ == "__main__":
    db_session.global_init("db/detector.db")
    app.run(host="0.0.0.0", port=8080, debug=True)
