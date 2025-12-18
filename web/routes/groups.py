from flask import Blueprint, render_template

import db

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")

@groups_bp.route("/")
def groups():
    chats = db.get_chats()
    return render_template("groups.html", chats=chats)