import os
from urllib.parse import quote_plus


def _build_mysql_uri():
    """Build MySQL connection URI from environment variables."""
    # If DATABASE_URL is provided, use it directly
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Build URI from individual components
    user = os.getenv("DB_USER", "gembonganggeredu")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "gembonganggeredu.mysql.pythonanywhere-services.com")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "gembonganggeredu$restaurant_db")

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
        "http://localhost:5173,http://127.0.0.1:5173,https://resto-manager.netlify.app",
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
    """Configuration for MySQL database (production - PythonAnywhere)."""

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


class PythonAnywhereConfig(MySQLConfig):
    """Configuration for PythonAnywhere production environment."""
    # Override defaults for PythonAnywhere
    pass


def get_config():
    """Get configuration class based on environment variables."""
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "mysql":
        return MySQLConfig
    elif db_type == "postgresql":
        return PostgreSQLConfig
    else:
        return SQLiteConfig


# Default configuration for PythonAnywhere production
Config = PythonAnywhereConfig
