import pytest
import json
from main import app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
def testLoginUserSuccess(client):
    """Test successful user login."""
    login_data = {
        "email": "marco.doe@example.com",
        "password": "securepassword"
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Login successful'
    assert 'user_id' in data

def testLoginUserMissingField(client):
    """Test login error for missing fields."""
    login_data = {
        "email": "marco.doe@example.com"
        # Password is missing
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email and password are required'

def testLoginUserInvalidEmailFormat(client):
    """Test login error for invalid email format."""
    login_data = {
        "email": "invalid-email-format",
        "password": "securepassword"
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email format'

def testLoginUserEmailNotFound(client):
    """Test login error for email not found."""
    login_data = {
        "email": "notfound@example.com",
        "password": "somepassword"
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email not found'

def testLoginUserIncorrectPassword(client):
    """Test login error for incorrect password."""
    login_data = {
        "email": "marco.doe@example.com",
        "password": "wrongpassword"
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Incorrect password'

