"""
enigma_logging.py — Central logging configuration for ENIGMA APEX

Call configure_logging() once at application startup (streamlit_app.py, app.py).
All other modules should use:

    import logging
    logger = logging.getLogger(__name__)

Environment variables:
    LOG_LEVEL   — DEBUG / INFO / WARNING / ERROR  (default: INFO)
    LOG_FILE    — path to log file                (default: enigma_apex.log)
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

_configured = False

LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_level: str = None, log_file: str = None) -> None:
    """Configure the root logger once for the whole application.

    Safe to call multiple times — subsequent calls are no-ops.
    """
    global _configured
    if _configured:
        return
    _configured = True

    level_name = log_level or os.environ.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)

    log_path = log_file or os.environ.get("LOG_FILE", "enigma_apex.log")

    root = logging.getLogger()
    root.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Stream handler — goes to stderr so it doesn't pollute Streamlit stdout
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    # Rotating file handler — 5 MB per file, keep 3 backups
    try:
        file_handler = RotatingFileHandler(
            log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root.addHandler(file_handler)
    except OSError:
        # Read-only filesystem (some cloud environments) — log to stream only
        logging.getLogger(__name__).warning(
            "Could not open log file %s — logging to stderr only", log_path
        )

    root.addHandler(stream_handler)

    # Suppress noisy third-party loggers at WARNING unless debug mode
    if level > logging.DEBUG:
        for noisy in ("websockets", "asyncio", "urllib3", "PIL"):
            logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper — equivalent to logging.getLogger(name)."""
    return logging.getLogger(name)
