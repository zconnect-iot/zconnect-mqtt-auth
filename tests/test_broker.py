import json
import uuid

import pytest
import mongoengine

from overlockmqttauth.brokers.vernemq import app
from overlockmqttauth.auth.mongodb.vmq import MQTTUser
# FIXME
from overlockmqttauth.auth.mongodb.overlock import Project


@pytest.fixture(name="test_client")
def fix_test_client():
    yield app.test_client()


def _getjson(response):
    try:
        return json.loads(response.data.decode("utf8"))
    except:
        return {}


class TestAuthRegisterByProject:

    def test_no_project(self, test_client):
        """no project in db - error"""
        response = test_client.post(
            "/auth_on_register",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
            }),
            content_type="application/json",
        )

        assert {"result": "error"} == _getjson(response)
        assert response._status_code == 200

    def test_with_project(self, test_client):
        """project exists, key doesn't match"""

        Project.objects().delete()
        p = Project(
            name="pid123",
            project_keys=[uuid.uuid4()],
        )
        p.save()

        response = test_client.post(
            "/auth_on_register",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
            }),
            content_type="application/json",
        )

        assert {"result": "error"} == _getjson(response)
        assert response._status_code == 200

    def test_with_project_key(self, test_client):
        """project exists, key matches"""

        Project.objects().delete()
        p = Project(
            name="pid123",
            project_keys=[uuid.uuid4()],
        )
        p.save()

        response = test_client.post(
            "/auth_on_register",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:{}".format(str(p.project_keys[0])),
                "client_id": "2of3opf23",
            }),
            content_type="application/json",
        )

        assert {"result": "next"} == _getjson(response)
        assert response._status_code == 200


class TestAuthRegisterByUser:

    @pytest.fixture(autouse=True)
    def fix_seed_db(self):
        MQTTUser(
          **{
            "username": "v1:pid123:aircon:0xbeef",
            "passhash": "$2a$12$G9/ZxPAMyPwiLCslezywge5WlHSHEU40XSV8ISPp04IN4K/rH4egW",
            "client_id": "fk4opgk4pokwep4otk490tk34t"
          }
        ).save()

        yield

        MQTTUser.objects().delete()

    @pytest.mark.xfail(reason="needs changing to do thiss tuff on pub/sub, not auth")
    def test_not_blacklisted(self, test_client):
        response = test_client.post(
            "/auth_on_register",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
            }),
            content_type="application/json",
        )

        assert {"result": "next"} == _getjson(response)
        assert response._status_code == 200

    def test_not_authed(self, test_client):
        response = test_client.post(
            "/auth_on_register",
            data=json.dumps({
                "username": "v1:pid123:blep:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
            }),
            content_type="application/json",
        )

        assert {"result": "error"} == _getjson(response)
        assert response._status_code == 200


class TestAuthPublish:

    def test_can_publish(self, test_client):
        response = test_client.post(
            "/auth_on_publish",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
                "topic": "/iot-2/type/gateway/id/v1:pid123:aircon:0xbeef/evt/boom/fmt/json",
            }),
            content_type="application/json",
        )

        assert {"result": "next"} == _getjson(response)
        assert response._status_code == 200

    def test_cant_publish_cmd(self, test_client):
        response = test_client.post(
            "/auth_on_publish",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
                "topic": "/iot-2/type/gateway/id/v1:pid123:aircon:0xbeef/cmd/boom/fmt/json",
            }),
            content_type="application/json",
        )

        assert {'result': {'error': 'Topic did not match regex'}} == _getjson(response)
        assert response._status_code == 200


class TestAuthSubscribe:

    def test_can_subscribe(self, test_client):
        response = test_client.post(
            "/auth_on_subscribe",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
                "topic": "/iot-2/type/gateway/id/v1:pid123:aircon:0xbeef/cmd/boom/fmt/json",
            }),
            content_type="application/json",
        )

        assert {"result": "next"} == _getjson(response)
        assert response._status_code == 200

    def test_cant_subscribe_evt(self, test_client):
        response = test_client.post(
            "/auth_on_subscribe",
            data=json.dumps({
                "username": "v1:pid123:aircon:0xbeef",
                "password": "p:abc",
                "client_id": "2of3opf23",
                "topic": "/iot-2/type/gateway/id/v1:pid123:aircon:0xbeef/evt/boom/fmt/json",
            }),
            content_type="application/json",
        )

        assert {'result': {'error': 'Topic did not match regex'}} == _getjson(response)
        assert response._status_code == 200

