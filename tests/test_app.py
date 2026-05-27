import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirect_to_index_html(self):
        # Arrange
        expected_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert expected_url in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for retrieving activities."""

    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_activity_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Drama Club",
            "Science Club",
            "Math Olympiad",
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert set(activities.keys()) == expected_activity_names

    def test_get_activities_includes_required_fields(self):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields


class TestSignupEndpoint:
    """Tests for student signup functionality."""

    def test_signup_for_activity_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_participant_returns_error(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipantEndpoint:
    """Tests for removing participants from activities."""

    def test_remove_participant_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_participant_returns_404(self):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
