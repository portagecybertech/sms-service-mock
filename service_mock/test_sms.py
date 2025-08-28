import os
from unittest import mock

from fastapi.testclient import TestClient

from .app import app

client = TestClient(app)


def test_sms_success():
    response = client.post(
        "/sms/send",
        data={
            "to_number": "+15558675309",
            "from_number": "+15017122661",
            "body": "Hi there!",
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert isinstance(resp, dict)
    assert resp["status"] == "success"
    assert resp["to_number"] == "+15558675309"
    assert resp["from_number"] == "+15017122661"
    assert resp["body"] == "Hi there!"
    assert "message_id" in resp
    assert resp["message_id"].startswith("mock-")


def test_sms_error_behavior():
    response = client.post(
        "/sms/send",
        data={
            "to_number": "+4291111111",
            "from_number": "+15017122661",
            "body": "Hi there!",
        },
    )
    assert response.status_code == 429
    resp = response.json()
    assert resp["status"] == "error"


def test_sms_error_behavior_disabled():
    with mock.patch.dict(os.environ, {"MOCK_ERROR_BEHAVIOR": "disabled"}):
        response = client.post(
            "/sms/send",
            data={
                "to_number": "+4291111111",
                "from_number": "+15017122661",
                "body": "Hi there!",
            },
        )
        assert response.status_code == 200


def test_sms_invalid_to_phone():
    response = client.post(
        "/sms/send",
        data={
            "to_number": "111",
            "from_number": "+15017122661",
            "body": "Hi there!",
        },
    )
    assert response.status_code == 400
    resp = response.json()
    assert isinstance(resp, dict)
    assert resp["status"] == "error"
    assert isinstance(resp.get("message"), str)
