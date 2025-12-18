from flask import (
    Blueprint, render_template, request,
    redirect, session, url_for
)
import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        admin = db.authenticate_webuser(login, password)

        if admin:
            session["web_user_id"] = admin["web_user_id"]
            session["web_user_login"] = admin["login"]
            return redirect(url_for("main.index"))

        return render_template(
            "login.html",
            error="Неверный логин или пароль"
        )

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
