"""Implements auth and management plugins for vernemq

Connects to the vmq broker as well because it needs to publish management events
to the broker when devices do certain things like registering

http://vernemq.com/docs/plugindevelopment/
"""

import logging
import os
import re

from flask import Flask, request, jsonify

from overlockmqttauth.connection import get_connection
from overlockmqttauth.auth.mongodb.util import mongo_connect
from .util import (InvalidClientId,
        exit_handler,
        enter_handler,
        client_id_to_org_type_id,
    )
from overlockmqttauth.client import client as mqttc

logger = logging.getLogger(__name__)


app = Flask(__name__)
mongo_connect()


PROJECT_PUB_REGEX = re.compile("""
    ^
    /iot-2
    /type/(?P<message_type>[^/]+)   # device type
    /id/(?P<auto_id>                # full identifier for this device
        (?P<api_ver>v[0-9])         # api version - v1, v2, etc
        :(?P<project_id>\w+)        # project id
        :(?P<product_name>\w+)      # name of product (same as device type?)
        :(?P<client_node_id>\w+)    # 'device id'
    )
    /evt/(?P<event>)                # type of event?
    /fmt/json
    $""", re.VERBOSE)


@app.route("/auth_on_register", methods=["POST"])
def auth_on_register():
    """Called immediately on a new connection

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

    logger.debug("auth_on_register: %s", as_json)

    connection = get_connection(
        as_json["username"],
        as_json["password"],
        as_json["client_id"],
    )

    response = {
        "result": "next"
    }

    if connection.blacklisted:
        logger.info("User has been blacklisted")

        response = {
            "result": "error"
        }

    if not connection.authenticated:
        logger.info("Could not find user with given username/pw")

        response = {
            "result": "error"
        }

    return jsonify(response)


@app.route('/auth_on_publish', methods=['POST'])
def auth_on_publish():
    """Restricts access to publishing messages

    Devices should only be able to publish to the 'event' topic for that
    project, not the 'command' topic

    > Note, in the example below the payload is not base64 encoded which is not
    > the default.

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
    """


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
    logging.basicConfig(level=logging.INFO)

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
