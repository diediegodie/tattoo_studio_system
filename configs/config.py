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
    """

    APP_NAME: str = "Tattoo Studio Manager"
    DEBUG: bool = True
    DATABASE_PATH: Path = Path("data/app.db")
    LOG_LEVEL: str = "INFO"
    TESTING: bool = False
    DB_URL: str = ""  # Will be set in __init__

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If TESTING is set (env or direct), use in-memory or temp DB
        if self.TESTING or str(os.environ.get("TESTING", "0")).lower() in (
            "1",
            "true",
            "yes",
        ):  # env override
            self.DB_URL = os.environ.get("DB_URL", "sqlite:///:memory:")
        else:
            self.DB_URL = f"sqlite:///{self.DATABASE_PATH}"
        # Log DB path for confirmation
        print(f"[AppConfig] Using DB_URL: {self.DB_URL}")


config = AppConfig()
