from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from app.config import Config


db = SQLAlchemy()

login_manager = LoginManager()


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load application configuration.
    app.config.from_object(Config)

    # Initialize Flask extensions.
    db.init_app(app)
    login_manager.init_app(app)

    # Flask-Login configuration.
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Import models so SQLAlchemy knows about them.
    from app import models

    # Load the logged-in user from the database.
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User

        return db.session.get(User, int(user_id))

    # Import application blueprints.
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.students import students_bp

    # Register application blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)

    # Database health check.
    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            database_status = "connected"
        except Exception as error:
            database_status = f"error: {error}"

        return {
            "status": "ok",
            "application": "SmartAttend",
            "database": database_status
        }

    return app
