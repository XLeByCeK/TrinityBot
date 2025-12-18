from .auth import auth_bp
from .main import main_bp
from .messages import messages_bp
from .groups import groups_bp
from .clients import clients_bp
from .users import users_bp
from .support import support_bp

def register_routes(app):

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(support_bp)