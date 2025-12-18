from flask import Blueprint, render_template, request

import db


messages_bp = Blueprint("messages", __name__, url_prefix="/messages")

@messages_bp.route("/", methods=["GET"])
def messages():

    filters = {
        "date_from": request.args.get("date_from"),
        "date_to": request.args.get("date_to"),
        "org_id": request.args.get("org_id"),
        "chat_id": request.args.get("chat_id"),
        "user": request.args.get("user"),
        "text": request.args.get("text"),
    }

    messages = db.get_messages_log(
        date_from=filters["date_from"],
        date_to=filters["date_to"],
        org_id=filters["org_id"],
        chat_id=filters["chat_id"],
        user_query=filters["user"],
        text_query=filters["text"],
    )

    orgs = db.get_organizations()

    return render_template(
        "messages.html",
        messages=messages,
        orgs=orgs,
        filters=filters
    )