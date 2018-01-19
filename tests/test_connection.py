from unittest.mock import patch
from overlockmqttauth.connection import get_connection


class TestConnection:

    def test_not_blacklisted(self):
        conn = get_connection(
            "v1:pid123:aircon:0xbeef",
            "p:abc",
            "2of3opf23",
        )

        assert not conn.blacklisted

    def test_blacklisted(self):
        conn = get_connection(
            "v1:pid123:aircon:0xbeef",
            "p:abc",
            "2of3opf23",
        )

        with patch("overlockmqttauth.auth.mongodb.vmq.VMQAuth.blacklisted", return_value=True):
            assert conn.blacklisted
