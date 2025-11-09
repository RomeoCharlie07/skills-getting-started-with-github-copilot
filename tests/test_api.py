"""
Tests for the main API endpoints of the Mergington High School Activities API.
"""

def test_root_redirect(client):
    """Test that root endpoint serves the static index.html content"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Mergington High School" in response.text


def test_get_activities_initial(client):
    """Test getting activities returns the initial activities plus added ones"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    
    # Check that we have at least the initial 3 activities
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    
    # Check that additional activities are added by the endpoint
    assert "Basketball Team" in activities
    assert "Swimming Club" in activities
    assert "Drama Club" in activities
    assert "Art Workshop" in activities
    assert "Math Olympiad" in activities
    assert "Science Club" in activities
    
    # Verify structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant(client):
    """Test that a student cannot sign up twice for the same activity"""
    # First signup should succeed
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student is already signed up for this activity"


def test_signup_existing_participant(client):
    """Test that existing participants cannot sign up again"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}  # Already in participants
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistration from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_participant(client):
    """Test unregistration of a student not registered for the activity"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_activity_data_structure(client):
    """Test that activity data has the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Check that max_participants is positive
        assert activity_data["max_participants"] > 0
        
        # Check that participants list contains valid email-like strings
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant


def test_multiple_signups_and_unregistrations(client):
    """Test multiple signup and unregistration operations"""
    # Sign up multiple students
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu", 
        "student3@mergington.edu"
    ]
    
    for student in students:
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": student}
        )
        assert response.status_code == 200
    
    # Verify all students are registered
    activities_response = client.get("/activities")
    activities = activities_response.json()
    programming_participants = activities["Programming Class"]["participants"]
    
    for student in students:
        assert student in programming_participants
    
    # Unregister one student
    response = client.delete(
        "/activities/Programming Class/unregister",
        params={"email": "student2@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify student was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    programming_participants = activities["Programming Class"]["participants"]
    
    assert "student1@mergington.edu" in programming_participants
    assert "student2@mergington.edu" not in programming_participants
    assert "student3@mergington.edu" in programming_participants