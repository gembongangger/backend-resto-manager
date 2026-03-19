import os
from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, jwt
from .routes import register_blueprints
from .models import User


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Ensure instance folder exists for sqlite and local config overrides.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_blueprints(app)

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
