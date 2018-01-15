from .api import parse_connection
from .auth import VMQAuth


class MQTTConnection:

    def __init__(self, username, password, client_id, api, auth):
        self._api = api(username, password, client_id)
        self._auth = auth(username, password, client_id)

    def api_version(self):
        """which connection api this is using

        Returns:
            int: enum corresponding to which connection version
        """

        return self._api.version

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

    def authorized(self):
        """Whether this connection is valid

        For it to be valid:
        - not blacklisted
        - in the project or device secrets (depending on secret type)

        Returns:
            bool: if this connection 'method' is valid
        """
        
        return self._auth.authorized

    def project_id(self):
        """Which project this connection corresponds to

        Returns:
            str: project id
        """

        return self._api.project_id

    def device_id(self):
        """Device id of connection

        Returns:
            str: device id
        """

        return self._api.device_id

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

    if auth_type is None:
        auth = VMQAuth(username, password, client_id)

    return MQTTConnection(api, auth)
