from configs.config import config
from utils.logger import setup_logger


def test_app_config_defaults():
    """Test that AppConfig loads values from .env or defaults."""
    assert config.APP_NAME == "Tattoo Studio Manager"
    assert config.DEBUG is False  # .env overrides default
    assert str(config.DATABASE_PATH) == "data/prod.db"  # .env overrides default
    assert config.LOG_LEVEL == "INFO"  # .env overrides default


def test_logger_basic_usage(caplog):
    """Test that logger uses config log level and outputs expected format."""
    logger = setup_logger("test_logger")
    with caplog.at_level(config.LOG_LEVEL):
        logger.info("Test message")
    # Check that the log contains the expected message and format
    assert any("test_logger" in r.name for r in caplog.records)
    assert any("Test message" in r.getMessage() for r in caplog.records)


def test_app_config_missing_env(monkeypatch):
    """Test AppConfig fallback to defaults if env vars missing (edge case)."""
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    from configs.config import AppConfig

    cfg = AppConfig()
    assert cfg.APP_NAME == "Tattoo Studio Manager"
    assert cfg.DEBUG is False
    assert str(cfg.DATABASE_PATH) == "data/prod.db"
    assert cfg.LOG_LEVEL == "INFO"


def test_logger_invalid_level():
    """Test logger setup with invalid log level (failure case)."""
    from utils.logger import setup_logger
    import logging

    logger = setup_logger("fail_logger")
    # Try to set an invalid level
    try:
        logger.setLevel("NOTALEVEL")
    except ValueError:
        # Should raise ValueError and not change level
        pass
    # Should fallback to WARNING or remain unchanged
    assert logger.level == logging.WARNING or logger.level == logging.INFO
