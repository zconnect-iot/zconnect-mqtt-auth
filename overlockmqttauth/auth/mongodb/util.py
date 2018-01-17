import logging
import os
import mongoengine


logger = logging.getLogger(__name__)


def mongo_connect():
    """Connect to mongodb

    Requires MONGO_HOST and MONGO_DATABASE, also takes port/ssl/etc.
    """
    try:
        mongo_settings = {
            "host": os.environ["MONGO_HOST"],
            "db": os.environ["MONGO_DATABASE"],
            "connect": False,
        }
    except KeyError as e:
        raise KeyError("Missing environment key") from e

    extra_settings = {
        "ssl": "MONGO_SSL",
        "username": "MONGO_USERNAME",
        "password": "MONGO_PASSWORD",
        "connect": "MONGO_CONNECT",
        "appname": "MONGO_APPNAME",
    }

    for setting, envvar in extra_settings.items():
        try:
            mongo_settings.update(**{setting: os.environ[envvar]})
        except KeyError:
            pass

    # Has to be an int
    try:
        mongo_settings.update(port=int(os.environ["MONGO_PORT"]))
    except KeyError:
        pass

    logger.info("Connecting to %s on %s", mongo_settings["db"], mongo_settings["host"])

    mongoengine.connect(**mongo_settings)
