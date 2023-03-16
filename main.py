from flask import Flask, request, render_template, redirect, abort, flash
from flask_login import LoginManager, login_user, logout_user, login_required, \
    current_user

from werkzeug.security import generate_password_hash, check_password_hash

from data import db_api
from data.users import User
from data import db_session

import datetime
import logging
import os

from tester.rating import UchebaParser

AVATAR_TYPES = ["png", "jpg", "jpeg", "gif"]
MEDIA_PIC_TYPES = ["png", "jpg", "jpeg", "gif"]
MEDIA_VID_TYPES = ["webm", "mp4"]
MEDIA_AUD_TYPES = ["mp3", "wav"]
MEDIA_TYPES = MEDIA_VID_TYPES + MEDIA_PIC_TYPES + MEDIA_AUD_TYPES


# logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s]'
# u' %(levelname)-8s [%(asctime)s] %(message)s',
# level=logging.DEBUG,
# filename='website-logging.log',
# filemode='w')


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
    if password.split():
        return True
    return False


def allowed_type(filename, types):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in types


app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/from_users'
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024


@app.route("/popular", methods=["GET"])
def popular_page():
    if current_user.is_authenticated:
        name = ['название'] + db.get_requests_types()

        total = db.get_popular()
        total = {(x[0], x[1], n): x[-1] for n, x in total.items()}
        slovar_total = list(total.keys())
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template("popular.html", current_user=current_user,
                               user=user, total=total, name=name,
                               slovar_total=slovar_total, number=len(name),
                               number2=len(slovar_total))
    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if current_user.is_authenticated:
            name = ['название'] + db.get_requests_types() + ["удалить"]
            total = db.requests_by_user_id(current_user.id)
            total = {(x[0], x[1], n): x[-1] for n, x in total.items()}
            slovar_total = list(total.keys())
            non_moder = db.non_moderated_by_user_id(current_user.id)
            reject = db.rejected_by_user_id(current_user.id)
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(
                User.id == current_user.id).first()
            return render_template("index.html", url=slovar_total, current_user=current_user,
                                   user=user, total=total, name=name,
                                   slovar_total=slovar_total, number=len(name),
                                   number2=len(slovar_total),
                                   non_moder=non_moder,
                                   number3=len(non_moder),
                                   non_moder_keys=list(non_moder.keys()),
                                   number4=len(reject), reject=reject,
                                   reject_keys=list(reject.keys()))
        return redirect("/login")
    elif request.method == "POST":
        site_id = list(request.form)[0].split()[0]
        db.del_site_by_user_id(site_id, current_user.id)
        flash("Сайт удален", "success")
        return redirect("/")


@app.route("/add_a_website", methods=["GET", "POST"])
@login_required
def add_a_website():
    if request.method == "GET":
        return render_template("add.html")
    elif request.method == "POST":
        if request.form.get("url") and request.form.get("name"):
            url = request.form["url"]
            if "https://" not in url:
                url = "https://" + request.form["url"]

            db.add_site((url, request.form["name"], request.form.get("email", ""), request.form.get("tg_id", "")),
                        current_user.id)
            flash("Сайт добавлен", "success")
            return redirect("/")
        else:
            return redirect("/add_a_website")


@app.route("/rating", methods=["GET"])
def rating():
    return render_template("rating.html")


@app.route("/report", methods=["GET"])
def report():
    return render_template("report.html")


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


@app.route("/site_repost", methods=["POST", "GET"])
def site_repost_page():
    return render_template("site_repost.html")


@app.route("/reject_rejection", methods=["GET", "POST"])
@login_required
def reject_rejection():
    if request.method == "GET":
        if not current_user.is_admin:
            abort(404)
        total = db.rejected_list()
        name = list(total.keys())
        return render_template("reject_rejection.html", reject_keys=name, number=len(name), reject=total)
    elif request.method == "POST":
        new_name = request.form["fname"]
        id_rating = request.form["id_rating"]
        d = list(request.form.keys())[1].split(" ")
        id_s, method = d[0], d[1]
        db.set_id_rating(id_rating, id_s)
        if method == "accept":
            db.set_moder((id_s, 1))
        db.set_name_for_site(id_s, new_name)
        flash("Сайт обработан!", "success")
        return redirect("/reject_rejection")


@app.route("/choice", methods=["GET"])
@login_required
def choice():
    if not current_user.is_admin:
        abort(404)
    return render_template("choice.html")


@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "GET":
        return render_template("reviews.html")
    elif request.method == "POST":
        comment = request.form["comment"]
        data = UchebaParser.search(comment  )
        return render_template("table_rating.html", data=data)


@app.route("/reject_moderation", methods=["GET", "POST"])
@login_required
def reject_moderation():
    if request.method == "GET":
        if not current_user.is_admin:
            abort(404)
        total = db.moderated_list()
        name = list(total.keys())
        return render_template("reject_moderation.html", reject_keys=name, number=len(name), reject=total)
    elif request.method == "POST":
        new_name = request.form["fname"]
        id_rating = request.form["id_rating"]
        d = list(request.form.keys())[1].split(" ")
        id_s, method = d[0], d[1]
        db.set_id_rating(id_rating, id_s)
        if method == "accept":
            db.set_moder((id_s, -1))
        db.set_name_for_site(id_s, new_name)
        flash("Сайт обработан!", "success")
        return redirect("/reject_moderation")


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_page():
    if request.method == "GET":
        if not current_user.is_admin:
            abort(404)
        total = db.non_moderated_list()
        name = list(total.keys())
        return render_template("admin.html", number=len(name), total=total,
                               name=name)
    elif request.method == "POST":
        new_name = request.form["fname"]
        id_rating = request.form["id_rating"]
        d = list(request.form.keys())[1].split(" ")
        id_s, method = d[0], d[1]
        db.set_id_rating(id_rating, id_s)
        if method == "accept":
            db.set_moder((id_s, 1))
        else:
            db.set_moder((id_s, -1))
        db.set_name_for_site(id_s, new_name)
        flash("Сайт обработан!", "success")
        return redirect("/")


@app.route("/statistic/<int:site_id>", methods=["GET", "POST"])
@login_required
def statistic_page(site_id):
    total = db.get_statistic(site_id)
    popular = db.connect(
            """SELECT id from sites WHERE is_moderated=1 ORDER BY id LIMIT 3""",
            fetchall=True)
    if not db.connect("""SELECT user_id, site_id FROM users_sites WHERE user_id=? AND
                                            site_id=?;""",
                      params=(current_user.id, site_id),
                      fetchall=True) and (site_id, ) not in popular:
        abort(404)
    d = db.connect("""SELECT name, url, id FROM sites WHERE id=? AND
                                            is_moderated=1;""",
                   params=(site_id,),
                   fetchall=True)
    if not d:
        abort(404)
    name_site, url_site, rate_id = d[0]
    rate = db.connect("""SELECT rating FROM rating
     WHERE site_id=?""", params=(rate_id, ),
                      fetchall=True)
    rate = rate[0][0] if rate else None
    if request.method == "GET":
        return render_template("report.html", total=total, url=url_site,
                           name=name_site, rate=rate)
    if request.method == "POST":
        d = list(request.form.keys())
        if d == ['feedback']:
            return render_template("report.html", total=total, url=url_site,
                           name=name_site)
        if d == ['rating']:
            return render_template("report.html", total=total, url=url_site,
                           name=name_site)


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
    app.run(host="0.0.0.0", port=8080, debug=False)
