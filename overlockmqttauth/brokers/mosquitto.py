# pylint: skip-file

"""Functions defined as described in https://github.com/mbachry/mosquitto_pyauth

Could also use these functions in future:
https://github.com/mbachry/mosquitto_pyauth#auxiliary-module
"""

import logging
import mosquitto_auth
from .connections import parse_connection


logger = logging.getLogger(__name__)


def plugin_init(opts):
    """called on plugin init, opts holds a tuple of (key, value) 2-tuples with
    all auth_opt_ params from mosquitto configuration (except
    auth_opt_pyauth_module)
    """

def plugin_cleanup():
    """called on plugin cleanup with no arguments
    """

def unpwd_check(username, password):
    """return True if given username and password pair is allowed to log in
    """
    connection = parse_connection(username, password)

    if connection.authorized:
        return True
    else:
        logger.error("Unauthorized user - blacklisted == %s", connection.blacklisted)

        return False

def acl_check(clientid, username, topic, access):
    """return True if given user is allowed to subscribe (access =
    mosquitto_auth.MOSQ_ACL_READ) or publish (access =
    mosquitto_auth.MOSQ_ACL_WRITE) to given topic (see mosquitto_auth module
    below)
    """

def psk_key_get(identity, hint):
    """return PSK string (in hex format without heading 0x) if given identity
    and hint pair is allowed to connect else return False or None
    """

def security_init(opts, reload):
    """called on plugin init and on config reload"""

def security_cleanup(reload):
    """called on plugin cleanup and on config reload"""
