from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.before_request
def check_auth():

    if not session.get("web_user_id"):
        
        return redirect(url_for("auth.login"))

@main_bp.route("/")
def index():

    return render_template("main.html")