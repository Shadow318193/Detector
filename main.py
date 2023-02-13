from flask import Flask, request, render_template, redirect, abort, flash
from flask_login import LoginManager, login_user, logout_user, login_required, \
    current_user

from werkzeug.security import generate_password_hash, check_password_hash

from data import db_api
from data.users import User
from data import db_session

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
login_manager.login_message = "Cмотреть данную страницу/делать данное " \
                              "действие можно " \
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


def password_is_correct(password: str):
    if password.islower() or password.isupper() or len(password) < 8:
        return False
    for i in password.lower():
        if i not in "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклм" \
                    "нопрстуфхцчшщъыьэюя0123456789!@$#_":
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


def allowed_type(filename, types):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in types


app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/from_users'
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024


@app.route("/", methods=["GET"])
def index():
    name = ['url']

    total = {'1': {'RU request': '100',
                   'US': '0',
                   'PO': '4',
                   'Статус модерации': 'eeee'},
             '2': {'RU request': '100',
                   'US': '0',
                   'PO': '4',
                   'Статус модерации': 'neeee'},
             '3': {'RU request': '100',
                   'US': '0',
                   'PO': '4',
                   'Статус модерации': 'Бааааан'},
             '4': {'RU request': '100',
                   'US': '0',
                   'PO': '4',
                   'Статус модерации': 'Бааааан'}}
    slovar_total = ['1', '2', '3', '4']
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template("index (1).html", current_user=current_user, user=user, total=total, name=name,
                               slovar_total=slovar_total, number=len(name), number2 = len(slovar_total))
    return redirect("/login")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect("/")
        return render_template("signup.html")
    elif request.method == "POST":
        if not name_is_correct(request.form["name"]):
            flash("Ошибка регистрации: имя не удовлетворяет требованию",
                  "danger")
            return redirect("/signup")
        elif not name_is_correct(request.form["surname"]):
            flash("Ошибка регистрации: фамилия не удовлетворяет требованию",
                  "danger")
            return redirect("/signup")
        elif not request.form["email"]:
            flash(
                "Ошибка регистрации: электронная почта "
                "не удовлетворяет требованию",
                "danger")
            return redirect("/signup")
        if request.form["password"] == request.form[
            "password_sec"] and password_is_correct(request.form["password"]):
            db_sess = db_session.create_session()
            c = db_sess.query(User).count()
            if c:
                existing_user = db_sess.query(User).filter(
                    User.email == request.form["email"]).first()
                if existing_user:
                    flash("Ошибка регистрации: кто-то уже есть с такой почтой",
                          "danger")
                    return redirect("/signup")
            user = User()
            user.name = request.form["name"]
            user.surname = request.form["surname"]
            user.email = request.form["email"]
            user.hashed_password = generate_password_hash(
                request.form["password"])
            if not c:
                user.is_admin = True
            else:
                user.is_admin = False
            db_sess.add(user)
            db_sess.commit()
            login_user(user)
            flash("Регистрация прошла успешно!", "success")
            return redirect("/")
        elif password_is_correct(request.form["password"]):
            flash("Ошибка регистрации: пароль не повторён", "danger")
            return redirect("/signup")
        else:
            flash("Ошибка регистрации: пароль не удовлетворяет требованию",
                  "danger")
            return redirect("/signup")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect("/")
        return render_template("login.html")
    elif request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == request.form["login"]).first()
        if user and check_password_hash(user.hashed_password,
                                        request.form["password"]):
            login_user(user)
            user.last_auth = datetime.datetime.now()
            flash("Успешный вход", "success")
            return redirect("/")
        elif not user:
            flash("Ошибка входа: неверный логин", "danger")
            return redirect("/login")
        elif not check_password_hash(user.hashed_password,
                                     request.form["password"]):
            flash("Ошибка входа: неверный пароль", "danger")
            return redirect("/login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_site", methods=["POST", "GET"])
def add_site_page():
    return render_template("add_site.html")


@app.route("/site_repost", methods=["POST", "GET"])
def site_repost_page():
    return render_template("site_repost.html")


@app.route("/popular", methods=["POST", "GET"])
def popular_page():
    return render_template("popular.html")


@app.route("/admin", methods=["POST", "GET"])
def admin_page():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template("admin.html")
        else:
            abort(403)
    else:
        abort(401)


@app.errorhandler(401)
def e401(code):
    print(code)
    flash("[Ошибка 401] " + login_manager.login_message, "warning")
    return redirect("/")


@app.errorhandler(403)
def e403(code):
    print(code)
    flash(
        "[Ошибка 403] Cмотреть данную страницу/делать данное действие "
        "можно только администраторам", "warning")
    return redirect("/")


@app.errorhandler(404)
def e404(code):
    print(code)
    return render_template("error.html", current_user=current_user,
                           code=404,
                           err="Мы не можем показать эту страницу: "
                               "её не существует")


@app.errorhandler(500)
def e500(code):
    print(code)
    return render_template("error.html", current_user=current_user, code=500,
                           err="Извините за неудобство. "
                               "Сейчас мы активно работаем над причиной "
                               "проблемы и исправляем её")


if __name__ == "__main__":
    db = db_api.DB("./db", "detector2.db")
    db.global_init()
    db_session.global_init("db/detector2.db")
    app.run(host="0.0.0.0", port=8080, debug=True)
