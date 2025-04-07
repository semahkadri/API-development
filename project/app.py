from flask import Flask
import config
from db.models import db
import routes
import logging

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, static_folder="static")
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    app.register_blueprint(routes.api_bp)

    with app.app_context():
        db.create_all()
        logger.info("Database and application initialized")

    return app

if __name__ == "__main__":
    app = create_app()
    logger.info("Starting application")
    app.run(debug=True, host="0.0.0.0", port=5000)