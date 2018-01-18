import logging
import json
from datetime import datetime
from overlockmqttauth.client import client as mqttc


logger = logging.getLogger(__name__)


class InvalidClientId(Exception):
    pass


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


def build_disconnect_status_payload(_request, dropped):
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
        'ClientID': _request.json['client_id'],
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
