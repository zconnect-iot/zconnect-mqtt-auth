import logging
from .v1 import V1API


logger = logging.getLogger(__name__)


def parse_connection(username, password):
    if username.startswith("v1"):
        return V1API(username, password)

    logger.error("Can't handle username '%s'", username)
    raise Exception("Invalid username")

__all__ = [
    "parse_connection",
]
