from .base import MQTTAPIVer


API_V1 = 1


class V1API(MQTTAPIVer):

    def __init__(self, user, password): #, client_id):
        self.user = user
        # self.client_id = client_id

        self._password = password
        (self._secret_type, self._secret) = password.split(":")
        (api_ver, self._project_id, self._product_name, self._device_id) = user.split(":")

        assert api_ver == "v1"

    @property
    def api_version(self):
        return API_V1

    # @property
    # def blacklisted(self):
    #     if self.secret_type == "p":
    #         project = projects[self._project_id]
    #         for secret in project.secrets:
    #             if (secret.val == self._secret) and secret.blacklisted:
    #                 return True
    #     else:
    #         for d in devices:
    #             if d.device_id == self.device_id \
    #             and d.secret.val == self._secret \
    #             and d.secret.blacklisted:
    #                 return True

    #     return False

    # @property
    # def authorized(self):
    #     if self.blacklisted:
    #         # blacklisted -> not authorised
    #         return False

    #     try:
    #         device = next(d for d in devices if d.device_id == self.device_id)
    #     except StopIteration:
    #         # doesn't exist -> not authorised
    #         return False

    #     try:
    #         project = next(p for p in projects if p.name == device.project)
    #     except StopIteration:
    #         # invalid project -> not authorised (this is a programming error
    #         # really)
    #         return False

    #     if device.secret.val == self._secret:
    #         # Already checked if its blacklisted
    #         return True

    #     for s in project.secrets:
    #         if s.val == self._secret:
    #             # Already checked if its blacklisted
    #             return True

    #     # doesn't match any secret -> not authorised
    #     return False

    @property
    def project_id(self):
        return self._project_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def secret_type(self):
        return self._secret_type
