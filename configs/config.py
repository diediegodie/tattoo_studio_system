from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class AppConfig(BaseSettings):
    """
    Configuration settings for the Tattoo Studio Manager application.

    Attributes:
        APP_NAME (str): The name of the application.
        DEBUG (bool): Flag to enable or disable debug mode.
        DATABASE_PATH (Path): Filesystem path to the application's database file.
        LOG_LEVEL (str): Logging level for the application.
        TESTING (bool): Flag to enable or disable testing mode.
        DB_URL (str): SQLAlchemy database URL (auto-set based on TESTING).
        JWT_SECRET_KEY (str): Secret key for JWT authentication.
    """

    APP_NAME: str = "Tattoo Studio Manager"
    DEBUG: bool = True
    DATABASE_PATH: Path = Path("data/app.db")
    LOG_LEVEL: str = "INFO"
    TESTING: bool = False
    DB_URL: str = ""  # Will be set in __init__
    JWT_SECRET_KEY: str = ""  # Should be set via environment variable or .env

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use DB_URL from env/.env if available, else fallback
        db_url_env = os.environ.get("DB_URL") or self.DB_URL
        if self.TESTING or str(os.environ.get("TESTING", "0")).lower() in (
            "1",
            "true",
            "yes",
        ):
            self.DB_URL = db_url_env or "sqlite:///:memory:"
        else:
            self.DB_URL = db_url_env or f"sqlite:///{self.DATABASE_PATH}"
        # Log DB path for confirmation
        print(f"[AppConfig] Using DB_URL: {self.DB_URL}")

        # Securely load JWT secret key
        if not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in environment or .env file.")


config = AppConfig()
