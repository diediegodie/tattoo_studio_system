# Step 3.3 – Configure Logging
# Make a reusable logging config file, e.g., utils/logger.py.

# Use log levels from the config file and format logs clearly:

import logging
from configs.config import config  # Reason: Use relative import as per project structure

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(config.LOG_LEVEL)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger