"""
Tests for activities endpoint (GET /activities)
"""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self, clean_client):
        """Test that GET /activities returns a 200 status code"""
        response = clean_client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, clean_client):
        """Test that GET /activities returns a dictionary of activities"""
        response = clean_client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_correct_activities(self, clean_client):
        """Test that the response contains the expected activities"""
        response = clean_client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Art Studio" in data

    def test_activity_has_required_fields(self, clean_client):
        """Test that each activity has all required fields"""
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        response = clean_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details, dict)
            assert required_fields.issubset(activity_details.keys())

    def test_activity_participants_is_list(self, clean_client):
        """Test that participants field is a list"""
        response = clean_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["participants"], list)
            assert all(isinstance(p, str) for p in activity_details["participants"])

    def test_activity_max_participants_is_integer(self, clean_client):
        """Test that max_participants is an integer"""
        response = clean_client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["max_participants"], int)
            assert activity_details["max_participants"] > 0

    def test_get_activities_preserves_existing_participants(self, clean_client):
        """Test that existing participants are returned correctly"""
        response = clean_client.get("/activities")
        data = response.json()
        
        assert "alice@test.edu" in data["Chess Club"]["participants"]
        assert "bob@test.edu" in data["Programming Class"]["participants"]
        assert "charlie@test.edu" in data["Programming Class"]["participants"]
        assert len(data["Art Studio"]["participants"]) == 0
