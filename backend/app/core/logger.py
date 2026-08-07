import logging
import sys

from app.core.config import settings

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        root = logging.getLogger()
        root.setLevel(settings.log_level.upper())
        root.addHandler(handler)
        _CONFIGURED = True
    return logging.getLogger(name)
