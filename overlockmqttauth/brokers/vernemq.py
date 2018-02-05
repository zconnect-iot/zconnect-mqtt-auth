"""Implements auth and management plugins for vernemq

Connects to the vmq broker as well because it needs to publish management events
to the broker when devices do certain things like registering

http://vernemq.com/docs/plugindevelopment/
"""

import logging
import logging.config
import os

import yaml
from flask import Flask, request, jsonify

from overlockmqttauth.connection import get_connection
from overlockmqttauth.auth.mongodb.util import mongo_connect
from overlockmqttauth.client import client as mqttc

from .util import (InvalidClientId,
        exit_handler,
        enter_handler,
        client_id_to_org_type_id,
        can_publish,
        can_subscribe,
        WORKER_PASSWORD,
        WORKER_USERNAME,
    )

logger = logging.getLogger(__name__)


app = Flask(__name__)
mongo_connect()


@app.route("/auth_on_register", methods=["POST"])
def auth_on_register():
    """Called immediately on a new connection

    If the username is 'overlock-worker', then the specific authorisation step
    is skipped and the OVERLOCK_WORKER_PASSWORD environment variable is used.

    http://vernemq.com/docs/plugindevelopment/sessionlifecycle.html

    Authorises against mongodb. vmq can't handle replicasets so do it here

    .. code-block:: python

        {
            "peer_addr": "127.0.0.1",
            "peer_port": 8888,
            "username": "username",
            "password": "password",
            "mountpoint": "",
            "client_id": "clientid",
            "clean_session": false
        }

    """

    as_json = request.json

    logger.info("auth_on_register: %s", as_json)

    response = {
        "result": "ok"
    }

    if as_json.get("username") == WORKER_USERNAME:
        if WORKER_PASSWORD is None:
            logger.warning("No OVERLOCK_WORKER_PASSWORD env set - ignoring worker auth")
        elif as_json["password"] == WORKER_PASSWORD:
            logger.info("Worker connected")
            return jsonify(response)

    try:
        connection = get_connection(
            as_json["username"],
            as_json["password"],
            as_json["client_id"],
        )
    except Exception: # pylint: disable=broad-except
        logger.exception("error parsing connection")

        response = {
            "result": {
                "error": "Unable to parse connection details",
            }
        }

    else:
        if not connection.authenticated:
            logger.info("Could not find user with given username/pw")

            response = {
                "result": {
                    "error": "Couldn't authenticate connection details",
                }
            }
        elif connection.blacklisted:
            logger.info("User has been blacklisted")

            response = {
                "result": {
                    "error": "User blacklisted",
                }
            }

    return jsonify(response)


@app.route('/auth_on_publish', methods=['POST'])
def auth_on_publish():
    """Restricts access to publishing messages

    Devices should only be able to publish to the 'event' topic for that
    project, not the 'command' topic

    > Note, in the example below the payload is not base64 encoded which is not
    > the default.

    Note:

        In the documentation, it says this is the payload:

            .. code-block:: python

                {
                    "username": "username",
                    "client_id": "clientid",
                    "mountpoint": "",
                    "qos": 1,
                    "topic": "a/b",
                    "payload": "hello",
                    "retain": false
                }

        But ACTUALLY it's this:

            .. code-block:: python

                {
                    "username": "username",
                    "client_id": "clientid",
                    "mountpoint": "",
                    "topics": [
                        {
                            "qos": 1,
                            "topic": "a/b",
                        },
                        {
                            "qos": 0,
                            "topic": "c/d",
                        }
                    ],
                }
    """

    as_json = request.json

    response = can_publish(as_json)

    return jsonify(response)


@app.route('/auth_on_subscribe', methods=['POST'])
def auth_on_subscribe():
    """Restricts access to subscribing to topics

    the rest is as above
    """

    as_json = request.json

    response = can_subscribe(as_json)

    return jsonify(response)


@app.route('/on_register', methods=['POST'])
def on_register():
    """Called when it's registered, but after auth_on_register

    This is used to actually handle any actions on registering

    .. code-block:: python

        {
            "peer_addr": "127.0.0.1",
            "peer_port": 8888,
            "username": "username",
            "mountpoint": "",
            "client_id": "clientid"
        }
    """
    response = {
        "result": "next"
    }

    client_id = request.json['client_id']
    logger.info("on_register request.json = %s", str(request.json))

    if client_id.startswith('controller'):
        return jsonify(response)

    try:
        logger.info("New client: %s", client_id_to_org_type_id(client_id))
    except InvalidClientId:
        logger.warning("Invalid client id received: %s", client_id)

    enter_handler(request)

    return jsonify(response)


@app.route('/on_client_gone', methods=['POST'])
def on_client_gone():
    """Client gone

    .. code-block:: python

        {
            "client_id": "clientid",
            "mountpoint": ""
        }
    """

    response = {
            "result": "next"
    }

    logger.info("on_client_gone request.json = %s", str(request.json))
    logger.info("Client Dropped: %s", request.json['client_id'])

    exit_handler(request, dropped=True)

    return jsonify(response)


@app.route('/on_client_offline', methods=['POST'])
def on_client_offline():
    """Client offline

    .. code-block:: python

        {
            "client_id": "clientid",
            "mountpoint": ""
        }
    """

    response = {
            "result": "next"
    }

    logger.info("on_client_offline request.json = %s", str(request.json))
    logger.info("Client Disconnect: %s", request.json['client_id'])

    exit_handler(request, dropped=False)

    return jsonify(response)


def start_broker():

    log_cfg = """
version: 1
formatters:
    google:
        (): overlockmqttauth.google_logging.GoogleFormatter
handlers:
    stderr:
        class: logging.StreamHandler
        formatter: google
loggers:
    overlockmqttauth:
        handlers:
            - stderr
        level: DEBUG
        propagate: False
"""

    as_dict = yaml.load(log_cfg)
    logging.config.dictConfig(as_dict)

    mqtt_host = os.getenv('MQTT_HOST', "localhost")
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    logger.info("Connecting to MQTT %s on port %s",
        mqtt_host, mqtt_port
    )
    mqttc.loop_start()
    mqttc.connect_async(mqtt_host, mqtt_port, 60)

    app.run(
        host=os.getenv('HOOK_HOST', '0.0.0.0'),
        port=int(os.getenv('HOOK_PORT', 5000)),
        debug=False,
    )
