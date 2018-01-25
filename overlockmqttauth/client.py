# pylint: skip-file

import os
import logging
import string
import random

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def mqtt_connect(client, userdata, flags, rc):
    logger.info("Connected to broker with result: %d", rc)
    if rc == 0:
        # To avoid disconnection, subscribe for something
        client.subscribe("$SYS/#")


def mqtt_log(client, userdata, level, buf):
    return
    logger.debug("MQTT: %s", buf)


def mqtt_message(client, userdata, msg):
    return
    logger.debug(msg.topic+" "+str(msg.payload))


def get_client():
    """Get basic mqtt client

    this doesn't make it connect or anything, just gets the client with all the
    callbacks and client_id set up.
    """
    mqttc = mqtt.Client(client_id="controller.{:s}".format(id_generator()), transport="websockets")

    username = os.getenv("VMQ_USERNAME", "overlock-worker")
    password = os.getenv("VMQ_PASSWORD", None)

    # Not setting TLS or anything - this should only be internal
    mqttc.username_pw_set(username, password)
    mqttc.on_log = mqtt_log
    mqttc.on_connect = mqtt_connect
    mqttc.on_message = mqtt_message

    return mqttc


client = get_client()
