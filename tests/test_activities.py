import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Store original state for reset between tests
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities database before each test."""
    for key in activities:
        activities[key] = copy.deepcopy(_original_activities[key])
    yield
    for key in activities:
        activities[key] = copy.deepcopy(_original_activities[key])


@pytest.fixture
def client():
    return TestClient(app)


# ---- GET /activities ----

class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange
        expected_activities = set(_original_activities.keys())

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert set(data.keys()) == expected_activities

    def test_activity_has_expected_structure(self, client):
        # Arrange
        required_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for name, details in data.items():
            assert required_keys.issubset(details.keys()), (
                f"Activity '{name}' is missing keys: {required_keys - set(details.keys())}"
            )
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)


# ---- POST /activities/{name}/signup ----

class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert new_email in response.json()["message"]
        # Verify participant was actually added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert new_email in participants

    def test_signup_nonexistent_activity(self, client):
        # Arrange
        fake_activity = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_email = _original_activities["Chess Club"]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


# ---- DELETE /activities/{name}/signup ----

class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_email = _original_activities["Chess Club"]["participants"][0]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email},
        )

        # Assert
        assert response.status_code == 200
        assert existing_email in response.json()["message"]
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert existing_email not in participants

    def test_unregister_nonexistent_activity(self, client):
        # Arrange
        fake_activity = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        unknown_email = "nobody@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": unknown_email},
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()


# ---- GET / ----

class TestRootRedirect:
    def test_root_redirects_to_index(self, client):
        # Arrange
        client = TestClient(app, follow_redirects=False)

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
