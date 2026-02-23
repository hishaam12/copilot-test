"""
Integration tests for complete user workflows
"""

import pytest


class TestIntegrationWorkflows:
    """Test complete user workflows across multiple endpoints"""

    def test_signup_and_verify_appears_in_list(self, clean_client):
        """Test that after signup, the participant appears in the activity list"""
        email = "jack@test.edu"
        activity = "Art Studio"
        
        # Sign up
        response = clean_client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify in list
        response = clean_client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_delete_and_verify_removed_from_list(self, clean_client):
        """Test the complete lifecycle: signup, then delete, then verify"""
        email = "kate@test.edu"
        activity = "Art Studio"
        
        # Sign up
        response = clean_client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify in list
        response = clean_client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Delete
        response = clean_client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants/{email.replace('@', '%40')}"
        )
        assert response.status_code == 200
        
        # Verify removed from list
        response = clean_client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_multiple_signups_and_deletions(self, clean_client):
        """Test complex workflow with multiple operations"""
        activity = "Art Studio"
        users = [
            ("leo@test.edu", "signup"),
            ("mia@test.edu", "signup"),
            ("leo@test.edu", "delete"),
            ("noah@test.edu", "signup"),
        ]
        
        for email, operation in users:
            if operation == "signup":
                response = clean_client.post(
                    f"/activities/{activity.replace(' ', '%20')}/signup",
                    params={"email": email}
                )
                assert response.status_code == 200
            else:
                response = clean_client.delete(
                    f"/activities/{activity.replace(' ', '%20')}/participants/{email.replace('@', '%40')}"
                )
                assert response.status_code == 200
        
        # Final verification
        response = clean_client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        assert "leo@test.edu" not in participants  # Was deleted
        assert "mia@test.edu" in participants      # Was added
        assert "noah@test.edu" in participants     # Was added

    def test_signup_for_multiple_activities(self, clean_client):
        """Test that a user can sign up for multiple different activities"""
        email = "olivia@test.edu"
        activities = ["Chess Club", "Art Studio"]
        
        # Sign up for each activity
        for activity in activities:
            response = clean_client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify in all activities
        response = clean_client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]

    def test_error_recovery_workflow(self, clean_client):
        """Test recovery from errors in the workflow"""
        email = "paul@test.edu"
        activity = "Art Studio"
        
        # Try to sign up twice - second should fail
        response1 = clean_client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = clean_client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        
        # Delete should still work
        response = clean_client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants/{email.replace('@', '%40')}"
        )
        assert response.status_code == 200
        
        # Try to delete again - should fail
        response = clean_client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants/{email.replace('@', '%40')}"
        )
        assert response.status_code == 404

    def test_preserves_other_participants_when_deleting_one(self, clean_client):
        """Test that deleting one participant doesn't affect others"""
        activity = "Programming Class"
        
        # Get initial participants
        response = clean_client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        assert len(initial_participants) >= 2
        
        # Delete one
        participant_to_delete = initial_participants[0]
        clean_client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants/{participant_to_delete.replace('@', '%40')}"
        )
        
        # Verify the others are still there
        response = clean_client.get("/activities")
        remaining = response.json()[activity]["participants"]
        
        assert participant_to_delete not in remaining
        for participant in initial_participants[1:]:
            assert participant in remaining
