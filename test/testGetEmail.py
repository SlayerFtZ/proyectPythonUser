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

def testGetUserByEmailSuccess(client):
    """Test successful retrieval of user data by email."""
    email = "marco.doe@example.com"
    response = client.get(f'/User/email/{email}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'first_name' in data
    assert data['first_name'] == "Marco Antonio"
    assert 'email' in data
    assert data['email'] == email

def testGetUserByEmailNotFound(client):
    """Test retrieval error for non-existent email."""
    email = "notfound@example.com"
    response = client.get(f'/User/email/{email}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'User not found'

def testGetUserByEmailInvalidFormat(client):
    """Test retrieval error for invalid email format."""
    email = "marco.doeexample.com"
    response = client.get(f'/User/email/{email}')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email format'

def testGetUserByEmailDatabaseError(client, mocker):
    """Test server error due to database connection issues."""
    mocker.patch('main.connectdataBase', return_value=None)
    
    email = "marco.antonio@example.com"
    response = client.get(f'/User/email/{email}')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Database connection error'
