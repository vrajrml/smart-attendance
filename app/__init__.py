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

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    login_manager.login_message = (
        "Please log in to access this page."
    )

    login_manager.login_message_category = "warning"


    from app import models


    @login_manager.user_loader
    def load_user(user_id):

        from app.models import User

        return db.session.get(
            User,
            int(user_id)
        )


    # =====================================================
    # BLUEPRINTS
    # =====================================================

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.students import students_bp
    from app.routes.subjects import subjects_bp
    from app.routes.class_sessions import class_sessions_bp
    from app.routes.attendance import attendance_bp
    from app.routes.reports import reports_bp


    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        students_bp
    )

    app.register_blueprint(
        subjects_bp
    )

    app.register_blueprint(
        class_sessions_bp
    )

    app.register_blueprint(
        attendance_bp
    )

    app.register_blueprint(
        reports_bp
    )


    # =====================================================
    # DATABASE HEALTH CHECK
    # =====================================================

    @app.route("/health")
    def health():

        try:

            db.session.execute(
                text("SELECT 1")
            )

            database_status = "connected"

        except Exception as error:

            database_status = (
                f"error: {error}"
            )

        return {
            "status": "ok",
            "application": "SmartAttend",
            "database": database_status
        }


    return app