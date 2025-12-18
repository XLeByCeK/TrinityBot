from flask import Blueprint, render_template, request

import db

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
def clients():

    search = request.args.get("q")

    orgs = db.get_clients(search)

    return render_template("clients.html", orgs=orgs, search=search)