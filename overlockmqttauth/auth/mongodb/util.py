import os
import mongoengine


def mongo_connect():
    """Connect to mongodb

    Requires MONGO_HOST and MONGO_DATABASE, also takes port/ssl/etc.
    """
    try:
        mongo_settings = {
            "mongo_host": os.environ["MONGO_HOST"],
            "mongo_db": os.environ["MONGO_DATABASE"],
            "connect": False,
        }
    except KeyError as e:
        raise KeyError("Missing environment key") from e

    extra_settings = {
        "port": "MONGO_PORT",
        "ssl": "MONGO_SSL",
        "username": "MONGO_USERNAME",
        "password": "MONGO_PASSWORD",
        "connect": "MONGO_CONNECT",
        "appname": "MONGO_APPNAME",
    }

    for setting, envvar in extra_settings:
        try:
            mongo_settings.update(**{setting: os.environ[envvar]})
        except KeyError:
            pass

    mongoengine.connect(**mongo_settings)
