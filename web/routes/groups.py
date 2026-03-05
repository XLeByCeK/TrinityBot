from flask import Blueprint, render_template, request, redirect, url_for

import db

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")

@groups_bp.route("/")
def groups():
    
    chats = db.get_chats()
    return render_template("groups.html", chats=chats)

@groups_bp.route("/update_report_type", methods=["POST"])
def update_report_type():

    max_chat_id = request.form.get("max_chat_id")
    report_type = request.form.get("report_type")
    
    if max_chat_id and report_type is not None:
        db.update_chat_report_type(int(max_chat_id), int(report_type))
        
    
    return redirect(url_for("groups.groups"))