"""
Backend Logging Configuration Module
Configures structured file and console logging for server operations and IP audit tracking.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from .config import LOGS_DIR, VIEWER_LOG_FILE, SERVER_LOG_FILE

# Ensure backend logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_backend_logger = None
_viewer_logger = None


def get_backend_logger() -> logging.Logger:
    """Returns the main application logger writing to backend/logs/server.log and stdout."""
    global _backend_logger
    if _backend_logger is not None:
        return _backend_logger

    logger = logging.getLogger("backend_server")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        file_handler = RotatingFileHandler(
            SERVER_LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    _backend_logger = logger
    return _backend_logger


def get_viewer_logger() -> logging.Logger:
    """Returns the dedicated viewer audit logger writing IP access events to backend/logs/viewer_audit.log."""
    global _viewer_logger
    if _viewer_logger is not None:
        return _viewer_logger

    logger = logging.getLogger("viewer_audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        file_handler = RotatingFileHandler(
            VIEWER_LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    _viewer_logger = logger
    return _viewer_logger
