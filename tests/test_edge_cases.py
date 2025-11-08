"""
Tests for edge cases and error handling in the Mergington High School Activities API.
"""

def test_signup_with_special_characters(client):
    """Test signup with special characters in email"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test+special@mergington.edu"}
    )
    assert response.status_code == 200


def test_signup_with_encoded_activity_name(client):
    """Test signup with URL-encoded activity name"""
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "encoded@mergington.edu"}
    )
    assert response.status_code == 200


def test_activity_case_sensitivity(client):
    """Test that activity names are case sensitive"""
    response = client.post(
        "/activities/chess club/signup",  # lowercase
        params={"email": "case@mergington.edu"}
    )
    assert response.status_code == 404


def test_empty_email_parameter(client):
    """Test signup with empty email parameter"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": ""}
    )
    # Should succeed as FastAPI doesn't validate email format by default
    assert response.status_code == 200


def test_missing_email_parameter(client):
    """Test signup without email parameter"""
    response = client.post("/activities/Chess Club/signup")
    assert response.status_code == 422  # Validation error


def test_activity_name_with_spaces(client):
    """Test that activity names with spaces work correctly"""
    activities = ["Chess Club", "Programming Class", "Gym Class"]
    
    for activity in activities:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": f"test-{activity.replace(' ', '-').lower()}@mergington.edu"}
        )
        assert response.status_code == 200


def test_long_email_address(client):
    """Test signup with very long email address"""
    long_email = "very" + "long" * 50 + "@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": long_email}
    )
    assert response.status_code == 200


def test_unregister_after_signup_in_same_session(client):
    """Test unregistering immediately after signing up"""
    email = "immediate@mergington.edu"
    
    # Sign up
    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Immediately unregister
    unregister_response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities["Chess Club"]["participants"]


def test_activities_endpoint_consistency(client):
    """Test that multiple calls to /activities return consistent data structure"""
    response1 = client.get("/activities")
    response2 = client.get("/activities")
    
    activities1 = response1.json()
    activities2 = response2.json()
    
    # Should have same keys
    assert set(activities1.keys()) == set(activities2.keys())
    
    # Each activity should have same structure
    for activity_name in activities1.keys():
        assert activities1[activity_name].keys() == activities2[activity_name].keys()


def test_concurrent_signups_different_activities(client):
    """Test signing up the same student for different activities"""
    email = "multisport@mergington.edu"
    activities = ["Chess Club", "Programming Class", "Gym Class"]
    
    for activity in activities:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is in all activities
    activities_response = client.get("/activities")
    all_activities = activities_response.json()
    
    for activity in activities:
        assert email in all_activities[activity]["participants"]