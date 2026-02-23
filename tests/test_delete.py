"""
Tests for delete participant endpoint (DELETE /activities/{activity_name}/participants/{email})
"""

import pytest


class TestDeleteParticipant:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_existing_participant_returns_200(self, clean_client):
        """Test that deleting an existing participant returns 200"""
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        assert response.status_code == 200

    def test_delete_returns_success_message(self, clean_client):
        """Test that delete returns a success message"""
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        data = response.json()
        assert "message" in data
        assert "alice@test.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_delete_removes_participant_from_activity(self, clean_client):
        """Test that the participant is actually removed from the activity"""
        email = "alice@test.edu"
        
        # Verify participant exists before delete
        response = clean_client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Delete
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = clean_client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]

    def test_delete_nonexistent_activity_returns_404(self, clean_client):
        """Test that deleting from a non-existent activity returns 404"""
        response = clean_client.delete(
            "/activities/Nonexistent%20Activity/participants/someone%40test.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_delete_nonexistent_participant_returns_404(self, clean_client):
        """Test that deleting a non-existent participant returns 404"""
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/nonexistent%40test.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_delete_decreases_participant_count(self, clean_client):
        """Test that delete decreases the participant count"""
        # Get initial count
        response = clean_client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        assert initial_count >= 1
        
        # Delete a participant
        clean_client.delete(
            "/activities/Programming%20Class/participants/bob%40test.edu"
        )
        
        # Get updated count
        response = clean_client.get("/activities")
        updated_count = len(response.json()["Programming Class"]["participants"])
        
        assert updated_count == initial_count - 1

    def test_delete_multiple_participants_same_activity(self, clean_client):
        """Test deleting multiple participants from the same activity"""
        # Programming Class has bob and charlie
        emails = ["bob@test.edu", "charlie@test.edu"]
        
        for email in emails:
            response = clean_client.delete(
                f"/activities/Programming%20Class/participants/{email.replace('@', '%40')}"
            )
            assert response.status_code == 200
        
        # Verify all were removed
        activities_response = clean_client.get("/activities")
        activities = activities_response.json()
        assert len(activities["Programming Class"]["participants"]) == 0

    def test_delete_participant_not_affected_other_activities(self, clean_client):
        """Test that deleting from one activity doesn't affect others"""
        # Delete from Chess Club
        clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        
        # Verify alice is still in other activities if applicable
        # (she's only in Chess Club in our test data, but verify Chess Club doesn't have her)
        activities_response = clean_client.get("/activities")
        activities = activities_response.json()
        assert "alice@test.edu" not in activities["Chess Club"]["participants"]
        # And other activities are unchanged
        assert activities["Programming Class"]["participants"] == ["bob@test.edu", "charlie@test.edu"]

    def test_cannot_delete_same_participant_twice(self, clean_client):
        """Test that deleting the same participant twice fails on second attempt"""
        email = "alice@test.edu"
        
        # First delete succeeds
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        assert response.status_code == 200
        
        # Second delete fails
        response = clean_client.delete(
            "/activities/Chess%20Club/participants/alice%40test.edu"
        )
        assert response.status_code == 404
