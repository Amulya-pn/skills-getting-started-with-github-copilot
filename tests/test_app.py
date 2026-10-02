from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == (
        "Learn strategies and compete in chess tournaments"
    )
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_new_participant(client):
    # Arrange
    url = "/activities/Soccer Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        url,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Soccer Club"
    }
    assert email in activities["Soccer Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    url = "/activities/Unknown Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        url,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    url = "/activities/Chess Club/signup"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        url,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_removes_existing_participant(client):
    # Arrange
    url = "/activities/Chess Club/participants/michael@mergington.edu"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    url = "/activities/Unknown Club/participants/student@mergington.edu"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant(client):
    # Arrange
    url = "/activities/Soccer Club/participants/student@mergington.edu"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}