from flask import Blueprint, render_template, request, redirect, url_for
import db
import commands

support_bp = Blueprint(
    "support",
    __name__,
    url_prefix="/support"
)

@support_bp.route("/", defaults={"chat_id": None}, methods=["GET", "POST"])
@support_bp.route("/<int:chat_id>", methods=["GET", "POST"])
def chat(chat_id):
 
    chats = db.get_support_chats()

    if chat_id is None and chats:
        chat_id = chats[0]["max_chat_id"]


    if chat_id:
        db.mark_support_handled(chat_id)


    messages = db.get_chat_messages(chat_id) if chat_id else []

    if request.method == "POST":
        text = request.form["message"]


        commands.send_message(chat_id, text)


        db.save_outgoing_message(chat_id, text)

        return redirect(url_for("support.chat", chat_id=chat_id))


    return render_template(
        "support_chat.html",
        chats=chats,
        messages=messages,
        active_chat=chat_id
    )
