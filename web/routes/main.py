from flask import Blueprint, render_template, session, redirect, url_for

import db

main_bp = Blueprint("main", __name__)

@main_bp.before_request
def check_auth():

    if not session.get("web_user_id"):
        
        return redirect(url_for("auth.login"))

@main_bp.route("/")
def index():

    new_support_requests = db.get_new_support_requests_count()

    return render_template("main.html", new_support_requests=new_support_requests)