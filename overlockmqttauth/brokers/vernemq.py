import logging
import string
import random
import json
import os
from datetime import datetime

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


mqttc = mqtt.Client(client_id="controller", transport="websockets")
app = Flask(__name__)


class InvalidClientId(Exception):
    pass


@app.route('/on_register', methods=['POST'])
def on_register():
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
    response = {
            "result": "next"
    }

    logger.info("on_client_gone request.json = %s", str(request.json))
    logger.info("Client Dropped: %s", request.json['client_id'])

    exit_handler(request, dropped=True)

    return jsonify(response)


@app.route('/on_client_offline', methods=['POST'])
def on_client_offline():
    response = {
            "result": "next"
    }

    logger.info("on_client_offline request.json = %s", str(request.json))
    logger.info("Client Disconnect: %s", request.json['client_id'])

    exit_handler(request, dropped=False)

    return jsonify(response)


def build_connect_status_payload(_request):
    """
    Build the connect status payload. It seems as though this is optional
    however the following keys are listed in the IBM documentation

        {
            'ClientAddr': '195.212.29.68',
            'Protocol': 'mqtt-tcp',
            'ClientID': 'd:bcaxk:psutil:001',
            'User': 'use-token-auth',
            'Time': '2014-07-07T06:37:56.494-04:00',
            'Action': 'Connect',
            'ConnectTime': '2014-07-07T06:37:56.493-04:00',
            'Port': 1883
        }

    For now, this is empty.
    """
    rq = _request.json
    return json.dumps({
        'ClientAddr': rq['peer_addr'],
        'Protocol': 'mqtt-tcp',
        'ClientID': rq['client_id'],
        'User': rq['username'],
        'Port': rq['peer_port'],
        'Action': 'Connect',
        'Time': datetime.utcnow().isoformat(),
    })


def build_disconnect_status_payload(request, dropped):
    """
    Build the disconnect status payload. It seems as though this is optional
    however the following keys are listed in the IBM documentation.

    The disconnect status can include all keys from the connect status

        {
            'WriteMsg': 0,
            'ReadMsg': 872,
            'Reason': 'The connection has completed normally.',
            'ReadBytes': 136507,
            'WriteBytes': 32,
        }

    For now, this is empty.
    """
    #  This is not a typo - disconnect status shares all the fields with connect
    return json.dumps({
        'Protocol': 'mqtt-tcp',
        'ClientID': request.json['client_id'],
        'Action': 'Disconnect',
        'Time': datetime.utcnow().isoformat(),
        'Reason': 'Peer disappeared' if dropped else 'Peer disconnected',
    })


def exit_handler(_request, dropped):
    logger.debug("Exit Handler")

    #  request.json = {'peer_port': 52294, 'mountpoint': '', 'username':
    #  'use-token-auth', 'peer_addr': '172.20.0.1', 'client_id':
    #  'g:abcdef:fridge:fridge-uuid1'}
    client_id = _request.json['client_id']

    if client_id.startswith('controller'):
        return

    try:
        org, device_type, device_id = client_id_to_org_type_id(client_id)
    except InvalidClientId:
        logger.warning("Invalid Client Id: %s", client_id)
        return

    topic = "iot-2/type/{}/id/{}/mon".format(device_type, device_id)

    payload = build_disconnect_status_payload(_request, dropped)
    logger.debug("Publishing MQTT")
    mqttc.publish(topic, payload)


def enter_handler(_request):
    logger.debug("Enter Handler")

    #  request.json = {'peer_port': 52294, 'mountpoint': '', 'username':
    #  'use-token-auth', 'peer_addr': '172.20.0.1', 'client_id':
    #  'g:abcdef:fridge:fridge-uuid1'}
    client_id = _request.json['client_id']

    if client_id.startswith('controller'):
        return

    try:
        org, device_type, device_id = client_id_to_org_type_id(client_id)
    except InvalidClientId:
        logger.warning("Invalid Client Id: %s", client_id)
        return

    topic = "iot-2/type/{}/id/{}/mon".format(device_type, device_id)

    payload = build_connect_status_payload(_request)
    logger.debug("Publishing MQTT")
    mqttc.publish(topic, payload)


def client_id_to_org_type_id(client_id):
    """
    Client ID should be a string: "g:" + self._options['org'] + ":" +
                            self._options['type'] + ":" + self._options['id'],

    """
    split = client_id.split(':')

    if len(split) != 4:
        raise InvalidClientId()

    org = split[1]
    device_type = split[2]
    device_id = split[3]

    return (org, device_type, device_id)


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    mqttc.username_pw_set("controller", "controller123")
    mqttc.on_log = mqtt_log
    mqttc.on_connect = mqtt_connect
    mqttc.on_message = mqtt_message
    # Connect
    mqtt_host = os.getenv('MQTT_HOST', "localhost")
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    logger.info("Connecting to MQTT {} on port {}".format(
        mqtt_host, mqtt_port
    ))
    mqttc.loop_start()
    mqttc.connect_async(mqtt_host, mqtt_port, 60)
    app.run(
        host=os.getenv('HOOK_HOST', '0.0.0.0'),
        port=int(os.getenv('HOOK_PORT', 5000)),
        debug=False,
    )
