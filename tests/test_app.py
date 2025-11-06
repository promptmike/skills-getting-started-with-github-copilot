import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # FastAPI's TestClient follows redirects by default
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_already_registered():
    # Try to sign up an already registered student
    email = "michael@mergington.edu"  # This email is already in Chess Club
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}

def test_signup_activity_not_found():
    response = client.post("/activities/NonexistentClub/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_remove_participant_success():
    # First add a participant
    email = "tempstudent@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then remove them
    response = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_remove_participant_not_found():
    response = client.delete("/activities/Chess Club/participants?email=nonexistent@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found for this activity"}

def test_remove_participant_activity_not_found():
    response = client.delete("/activities/NonexistentClub/participants?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}