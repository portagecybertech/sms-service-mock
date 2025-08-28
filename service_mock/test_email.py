import os
from unittest import mock

from fastapi.testclient import TestClient

from .app import app

client = TestClient(app)


def test_email_success():
    response = client.post(
        "/email/send",
        data={
            "message": """From: a@example.com
To: b@example.com
Subject: Test Email

Hello
"""
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert isinstance(resp, dict)
    assert resp["status"] == "success"
    assert resp["from_addr"] == "a@example.com"
    assert resp["to_addrs"] == ["b@example.com"]
    assert resp["subject"] == "Test Email"
    assert "message_id" in resp
    assert resp["message_id"].startswith("mock-")


def test_email_error_behavior():
    response = client.post(
        "/email/send",
        data={
            "message": """From: a@example.ca
To: b@example.com
Subject: Test Email

Hello
"""
        },
    )
    assert response.status_code == 429
    resp = response.json()
    assert resp["status"] == "error"


def test_email_error_behavior_disabled():
    with mock.patch.dict(os.environ, {"MOCK_ERROR_BEHAVIOR": "disabled"}):
        response = client.post(
            "/email/send",
            data={
                "message": """From: a@example.ca
To: b@example.com
Subject: Test Email

Hello
"""
            },
        )
        assert response.status_code == 200


def test_email_bad_from_addr():
    response = client.post(
        "/email/send",
        data={
            "message": """From: a@example....
To: b@example.com
Subject: Test Email

Hello
"""
        },
    )
    assert response.status_code == 400
    resp = response.json()
    assert isinstance(resp, dict)
    assert resp["status"] == "error"
    assert isinstance(resp.get("message"), str)
