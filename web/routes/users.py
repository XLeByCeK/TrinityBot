from flask import Blueprint, render_template, request
import db

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/")
def users():

    search = request.args.get("q")

    users = db.get_users(search)

    return render_template("users.html", users=users, search=search)