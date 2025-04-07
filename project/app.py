from flask import Flask
import config
import routes

def create_app() -> Flask:
    """Initialize and configure the Flask application."""
    app = Flask(__name__, static_folder="static")
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
    config.configure_dependencies()
    app.register_blueprint(routes.api_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)