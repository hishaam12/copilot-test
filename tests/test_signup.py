"""
Tests for signup endpoint (POST /activities/{activity_name}/signup)
"""

import pytest


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, clean_client):
        """Test that signing up a new participant returns 200"""
        response = clean_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "david@test.edu"}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, clean_client):
        """Test that signup returns a success message"""
        response = clean_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "david@test.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "david@test.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, clean_client):
        """Test that the participant is actually added to the activity"""
        email = "david@test.edu"
        
        # Signup
        response = clean_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = clean_client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_invalid_activity_returns_404(self, clean_client):
        """Test that signing up for a non-existent activity returns 404"""
        response = clean_client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "david@test.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, clean_client):
        """Test that signing up with an email already in the activity returns 400"""
        # Try to sign up alice again (she's already in Chess Club)
        response = clean_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "alice@test.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_multiple_participants_same_activity(self, clean_client):
        """Test signing up multiple different participants to the same activity"""
        emails = ["david@test.edu", "eve@test.edu", "frank@test.edu"]
        
        for email in emails:
            response = clean_client.post(
                "/activities/Art%20Studio/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = clean_client.get("/activities")
        activities = activities_response.json()
        for email in emails:
            assert email in activities["Art Studio"]["participants"]

    def test_signup_increases_participant_count(self, clean_client):
        """Test that signup increases the participant count"""
        # Get initial count
        response = clean_client.get("/activities")
        initial_count = len(response.json()["Art Studio"]["participants"])
        
        # Sign up new participant
        clean_client.post(
            "/activities/Art%20Studio/signup",
            params={"email": "grace@test.edu"}
        )
        
        # Get updated count
        response = clean_client.get("/activities")
        updated_count = len(response.json()["Art Studio"]["participants"])
        
        assert updated_count == initial_count + 1

    def test_signup_different_participants_different_activities(self, clean_client):
        """Test signing up different participants to different activities"""
        clean_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "henry@test.edu"}
        )
        clean_client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "iris@test.edu"}
        )
        
        # Verify correct assignments
        activities_response = clean_client.get("/activities")
        activities = activities_response.json()
        
        assert "henry@test.edu" in activities["Chess Club"]["participants"]
        assert "iris@test.edu" in activities["Programming Class"]["participants"]
        assert "iris@test.edu" not in activities["Chess Club"]["participants"]
        assert "henry@test.edu" not in activities["Programming Class"]["participants"]
