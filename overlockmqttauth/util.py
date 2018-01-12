from abc import ABCMeta, abstractproperty

from .auth_data import projects, devices


API_V1 = 1


class MQTTConnection(metaclass=ABCMeta):

    @abstractproperty
    def api_version(self):
        """which connection api this is using

        Returns:
            int: enum corresponding to which connection version
        """

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
    def authorized(self):
        """Whether this connection is valid

        For it to be valid:
        - not blacklisted
        - in the project or device secrets (depending on secret type)

        Returns:
            bool: if this connection 'method' is valid
        """

    @abstractproperty
    def project_id(self):
        """Which project this connection corresponds to

        Returns:
            str: project id
        """

    @abstractproperty
    def device_id(self):
        """Device id of connection

        Returns:
            str: device id
        """

    @abstractproperty
    def secret_type(self):
        """Type of secret used to authenticate

        Either a project wide secret or a device specific secret

        Returns:
            str: type of secret - 'p' for project secret, 'd' for device secret
        """


class V1Connection(MQTTConnection):

    def __init__(self, user, password, client_id):
        self.user = user
        self.client_id = client_id

        (self._secret_type, self._secret) = password
        (api_ver, self._project_id, self._device_id) = user.split(":")

        assert api_ver == "v1"

    @property
    def api_version(self):
        return API_V1

    @property
    def blacklisted(self):
        if self.secret_type == "p":
            project = projects[self._project_id]
            for secret in project.secrets:
                if (secret.val == self._secret) and secret.blacklisted:
                    return True
        else:
            for d in devices:
                if d.device_id == self.device_id \
                and d.secret.val == self._secret \
                and d.secret.blacklisted:
                    return True

        return False

    @property
    def authorized(self):
        if self.blacklisted:
            # blacklisted -> not authorised
            return False

        try:
            device = next(d for d in devices if d.device_id == self.device_id)
        except StopIteration:
            # doesn't exist -> not authorised
            return False

        try:
            project = next(p for p in projects if p.name == device.project)
        except StopIteration:
            # invalid project -> not authorised (this is a programming error
            # really)
            return False

        if device.secret.val == self._secret:
            # Already checked if its blacklisted
            return True

        for s in project.secrets:
            if s.val == self._secret:
                # Already checked if its blacklisted
                return True

        # doesn't match any secret -> not authorised
        return False

    @property
    def project_id(self):
        return self._project_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def secret_type(self):
        return self._secret_type
