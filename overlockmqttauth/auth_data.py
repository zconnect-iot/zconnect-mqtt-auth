class Secret:
    """Represents a device or project secret
    """
    def __init__(self, val, blacklisted):
        self.val = val
        self.blacklisted = blacklisted


projects = [
    {
        "name": "abc123",
        "secrets": [
            Secret("sdkg40wkgk3pok32", False),
            Secret("bm,vbmvbmvbcmmbn", False),
        ],
        "blacklisted": False,
    },
]


devices = [
    {
        "project": "abc123",
        "device_id": "blapt",
        "secret": Secret("2123122413423", False),
    },
]
