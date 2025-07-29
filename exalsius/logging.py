import logging
from typing import Optional

from termcolor import colored


class ColorFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self._formatters = {
            logging.DEBUG: logging.Formatter(
                colored("[%(asctime)s %(name)s]: ", "blue") + "%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            ),
            logging.INFO: logging.Formatter(
                colored("[%(asctime)s %(name)s]: ", "green") + "%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            ),
            logging.WARNING: logging.Formatter(
                colored("[%(asctime)s %(name)s]: ", "yellow") + "%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            ),
            logging.ERROR: logging.Formatter(
                colored("[%(asctime)s %(name)s]: ", "red") + "%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            ),
            logging.CRITICAL: logging.Formatter(
                colored("[%(asctime)s %(name)s]: ", "red", attrs=["bold"])
                + "%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            ),
        }

    def format(self, record):
        if record.name == "root":
            record.name = "cli"
        formatter = self._formatters.get(record.levelno, self._formatters[logging.INFO])
        return formatter.format(record)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    log_level = log_level.upper()
    level = getattr(logging, log_level, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ColorFormatter())
    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s %(name)s %(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
