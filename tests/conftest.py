"""
Pytest configuration and shared fixtures for backend tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provides a FastAPI TestClient for making requests"""
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Provides a fresh activities dictionary for each test.
    This ensures tests don't interfere with each other.
    """
    test_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 5,
            "participants": ["alice@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["bob@test.edu", "charlie@test.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": []
        }
    }
    
    # Replace the global activities dict with test data
    activities.clear()
    activities.update(test_data)
    
    yield activities
    
    # Cleanup: restore original data (optional, but good practice)
    activities.clear()


@pytest.fixture
def clean_client(test_activities):
    """
    Provides a TestClient with fresh test data for each test.
    Use this fixture when you need both the client and fresh test data.
    """
    return TestClient(app)
