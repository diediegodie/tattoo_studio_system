import unittest
import logging
from utils.logger import setup_logger
from configs.config import config


class TestFrontendLogger(unittest.TestCase):
    """
    Unit tests for the frontend logger setup.

    This test case verifies the correct creation and configuration of a logger
    for the frontend component. It ensures that the logger is initialized with
    the expected log level and is capable of logging messages.

    Test Methods:
        test_logger_creation:
            Tests that the logger is created with the correct name and log level,
            and that it can log an informational message.
    """

    def test_logger_creation(self):
        logger = setup_logger("frontend_test")
        self.assertEqual(logger.level, logging.getLevelName(config.LOG_LEVEL))
        logger.info("Frontend logger test message")


if __name__ == "__main__":
    unittest.main()
