class Secret:
    """Represents a device or project secret
    """
    def __init__(self, val, blacklisted):
        self.val = val
        self.blacklisted = blacklisted


class Project:
    def __init__(self, name, secrets, blacklisted):
        self.name = name
        self.secrets = secrets
        self.blacklisted = blacklisted


class Device:
    def __init__(self, project, device_id, secret):
        self.project = project
        self.device_id = device_id
        self.secret = secret


projects = [
    Project(
        "abc123",
        [
            Secret("sdkg40wkgk3pok32", False),
            Secret("bm,vbmvbmvbcmmbn", False),
        ],
        False,
    ),
]


devices = [
    Device(
        "abc123",
        "blapt",
        Secret("2123122413423", False),
    ),
]
