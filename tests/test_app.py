
from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def isolate_activities():
    """Sichere und stelle den globalen `activities`-Zustand wieder her."""
    original = deepcopy(app_module.activities)
    yield
    app_module.activities = original


client = TestClient(app_module.app)


def test_get_activities():
    # Arrange
    # (client fixture is available)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "tester@example.com"
    path = f"/activities/{quote(activity, safe='')}/signup"
    before = len(app_module.activities[activity]["participants"])

    # Act
    resp = client.post(path, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert len(app_module.activities[activity]["participants"]) == before + 1


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "dup@example.com"
    path = f"/activities/{quote(activity, safe='')}/signup"

    # Act
    resp1 = client.post(path, params={"email": email})
    resp2 = client.post(path, params={"email": email})

    # Assert
    assert resp1.status_code == 200
    assert resp2.status_code == 400


def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "remove@example.com"
    signup_path = f"/activities/{quote(activity, safe='')}/signup"
    delete_path = f"/activities/{quote(activity, safe='')}/participants"
    resp_signup = client.post(signup_path, params={"email": email})
    assert resp_signup.status_code == 200
    before = len(app_module.activities[activity]["participants"])

    # Act
    resp = client.delete(delete_path, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert len(app_module.activities[activity]["participants"]) == before - 1
    assert email not in app_module.activities[activity]["participants"]
