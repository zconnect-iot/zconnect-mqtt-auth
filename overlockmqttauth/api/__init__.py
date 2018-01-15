from .v1 import V1API


def parse_connection(username, password):
    if username.startswith("v1"):
        return V1API(username, password)
    else:
        raise Exception("Invalid username")

__all__ = [
    "parse_connection",
]
