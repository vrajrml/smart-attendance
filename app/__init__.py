from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from app.config import Config


db = SQLAlchemy()


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration.
    app.config.from_object(Config)

    # Initialize database.
    db.init_app(app)

    @app.route("/")
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartAttend</title>
        </head>
        <body>
            <h1>SmartAttend</h1>
            <p>Smart Attendance System is running.</p>
        </body>
        </html>
        """

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
