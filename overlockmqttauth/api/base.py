from abc import ABCMeta, abstractproperty


class MQTTAPIVer(metaclass=ABCMeta):

    @abstractproperty
    def api_version(self):
        """which connection api this is using

        Returns:
            int: enum corresponding to which connection version
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
