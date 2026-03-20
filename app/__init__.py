import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import get_config, BaseConfig, MySQLConfig, _load_env_file
from .extensions import db, migrate, jwt
from .routes import register_blueprints
from .models import User

# Auto-detect environment and load appropriate .env file
# Must be called before get_config()
env_detected = _load_env_file()
print(f"Environment detected: {env_detected}")


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    # Use provided config or auto-detect from environment
    if config_object is None:
        config_object = get_config()

    app.config.from_object(config_object)
    
    # Set database URI for MySQL config (build from env vars at runtime)
    if isinstance(config_object, type) and issubclass(config_object, MySQLConfig):
        app.config['SQLALCHEMY_DATABASE_URI'] = MySQLConfig.get_database_uri()
    elif config_object == MySQLConfig:
        app.config['SQLALCHEMY_DATABASE_URI'] = MySQLConfig.get_database_uri()

    CORS(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # Ensure instance folder exists for sqlite and local config overrides.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_blueprints(app)

    # Serve uploaded files
    @app.route("/uploads/<filename>")
    def serve_upload(filename):
        if os.path.exists("/home/gembonganggeredu"):
            # Production on PythonAnywhere
            upload_folder = "/home/gembonganggeredu/mysite/static/uploads"
        else:
            # Local development
            upload_folder = os.path.join(app.root_path, "static", "uploads")
        
        # Check if file exists
        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            from flask import abort
            abort(404)
        
        return send_from_directory(upload_folder, filename)

    @jwt.user_lookup_loader
    def load_user(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        return db.session.get(User, identity)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database tables."""
        db.create_all()
        print("Initialized the database.")

    return app
