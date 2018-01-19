from abc import ABCMeta, abstractproperty


class MQTTAuth(metaclass=ABCMeta):

    def __init__(self, username, password, client_id):
        self._username = username
        # FIXME
        _, self._password = password.split(":")
        self._client_id = client_id

    @abstractproperty
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

    @abstractproperty
    def authenticated(self):
        """Whether this connection is valid

        For it to be valid:
        - not blacklisted
        - in the project or device secrets (depending on secret type)

        Returns:
            bool: if this connection 'method' is valid
        """
