import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv


def _detect_environment():
    """
    Detect running environment and return the appropriate .env file path.
    - Production (PythonAnywhere): /home/gembonganggeredu/... or DB_HOST contains 'pythonanywhere'
    - Local: everything else
    """
    # Check for PythonAnywhere environment
    if os.path.exists("/home/gembonganggeredu"):
        return "production"

    # Check if already has DB_HOST set to PythonAnywhere
    db_host = os.getenv("DB_HOST", "")
    if "pythonanywhere" in db_host.lower():
        return "production"

    # Check for FLASK_ENV environment variable
    flask_env = os.getenv("FLASK_ENV", "development")
    if flask_env == "production":
        return "production"

    return "development"


def _load_env_file():
    """
    Load appropriate .env file based on detected environment.
    - Production: .env.production
    - Development: .env (default)
    """
    env = _detect_environment()

    # Get the project root directory (backend folder)
    # Navigate from app/config.py to backend/
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent  # backend/

    if env == "production":
        env_file = project_root / ".env.production"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return "production"
        else:
            # Fallback to .env if .env.production doesn't exist
            load_dotenv()
            return "development (fallback)"
    else:
        # Development - load .env
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
        return "development"


def _build_mysql_uri():
    """Build MySQL connection URI from environment variables."""
    # If DATABASE_URL is provided, use it directly
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Build URI from individual components
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "restaurant_db")

    # URL-encode password if it contains special characters
    encoded_password = quote_plus(password) if password else ""

    # Build connection string
    if encoded_password:
        return f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}?charset=utf8mb4"
    else:
        return f"mysql+pymysql://{user}@{host}:{port}/{database}?charset=utf8mb4"


class BaseConfig:
    """Base configuration with common settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    _cors_origins_raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://resto-manager.netlify.app,https://localhost",
    )
    CORS_ORIGINS = [
        origin.strip().rstrip("/")
        for origin in _cors_origins_raw.split(",")
        if origin.strip()
    ]

    # Image upload configuration
    IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    FREEIMAGE_API_KEY = os.getenv("FREEIMAGE_API_KEY")

    # Upload folder configuration
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static", "uploads")
    )


class SQLiteConfig(BaseConfig):
    """Configuration for SQLite database (development/testing)."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "timeout": 30,
            "check_same_thread": False,
        }
    }


class MySQLConfig(BaseConfig):
    """Configuration for MySQL database (production)."""

    @classmethod
    def get_database_uri(cls):
        """Get database URI, building it from env vars if needed."""
        return _build_mysql_uri()

    # Connection pool settings for MySQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "connect_args": {
            "charset": "utf8mb4",
            "use_unicode": True,
        }
    }


class PostgreSQLConfig(BaseConfig):
    """Configuration for PostgreSQL database (production)."""
    # PostgreSQL connection string format: postgresql://user:password@host:port/database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/resto_manager"
    )
    # Connection pool settings for PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }


def get_config():
    """Get configuration class based on environment variables."""
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "mysql":
        return MySQLConfig
    elif db_type == "postgresql":
        return PostgreSQLConfig
    else:
        return SQLiteConfig


# Default configuration for backward compatibility
Config = SQLiteConfig
