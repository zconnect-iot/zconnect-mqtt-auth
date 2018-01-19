import logging
from .api import parse_connection
from .auth.mongodb import VMQAuth


logger = logging.getLogger(__name__)


class MQTTConnection:

    def __init__(self, api, auth):
        self._api = api
        self._auth = auth

    @property
    def api_version(self):
        """which connection api this is using

        Returns:
            int: enum corresponding to which connection version
        """

        return self._api.version

    @property
    def blacklisted(self):
        """Whether this connection has been blacklisted

        Can be blacklisted on:
        - project secret (all devices using that secret)
        - per project (all devices)
        - per device

        This doesn't return whether a connection is authorised, only if it has
        EXPLICITLY been blacklisted

        Returns:
            bool: if this connection 'method' has been blacklisted
        """

        return self._auth.blacklisted

    @property
    def authenticated(self):
        """Whether this connection is by a valid user

        For it to be valid:
        - not blacklisted
        - in the project or device secrets (depending on secret type)

        Returns:
            bool: if the user is authenticated
        """

        return self._auth.authenticated

    def subscribe_authorized(self, topic):
        """Whether the user is allowed to subscribe to this topic

        Args:
            topic (str): topic to subsribe to

        Returns:
            bool: If the user is allowed to subcribe
        """

        return self._api.subscribe_authorized(topic)

    def publish_authorized(self, topic):
        """Whether the user is allowed to publish to this topic

        Args:
            topic (str): topic to publish to

        Returns:
            bool: If the user is allowed to publish to this topic
        """

        return self._api.publish_authorized(topic)

    @property
    def project_id(self):
        """Which project this connection corresponds to

        Returns:
            str: project id
        """

        return self._api.project_id

    @property
    def device_id(self):
        """Device id of connection

        Returns:
            str: device id
        """

        return self._api.device_id

    @property
    def secret_type(self):
        """Type of secret used to authenticate

        Either a project wide secret or a device specific secret

        Returns:
            str: type of secret - 'p' for project secret, 'd' for device secret
        """

        return self._api.secret_type


def get_connection(username, password, client_id, api_type=None, auth_type=None):
    if api_type is None:
        api = parse_connection(username, password)

    logger.debug("API = %s", api)

    if auth_type is None:
        auth = VMQAuth(username, password, client_id)

    logger.debug("Auth method = %s", auth)

    return MQTTConnection(api, auth)
