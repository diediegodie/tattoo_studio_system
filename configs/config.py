from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class AppConfig(BaseSettings):
    """
    Configuration settings for the Tattoo Studio Manager application.

    Attributes:
        APP_NAME (str): The name of the application.
        DEBUG (bool): Flag to enable or disable debug mode.
        DATABASE_PATH (Path): Filesystem path to the application's database file.
        LOG_LEVEL (str): Logging level for the application.
    """

    APP_NAME: str = "Tattoo Studio Manager"
    DEBUG: bool = True
    DATABASE_PATH: Path = Path("data/app.db")
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

config = AppConfig()
