"""
Main entry point for the Flask backend using the application factory pattern.
"""

import logging
from backend.app_factory import create_app

app = create_app()

if __name__ == "__main__":
    logging.info("Starting Tattoo Studio Management Flask backend (factory mode)")
    app.run(host="127.0.0.1", port=5000)
