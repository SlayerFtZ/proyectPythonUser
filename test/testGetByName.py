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
def testGetUserByNamesSuccess(client):
    """Test successful retrieval of user data by names."""
    # Assuming you have a user with these details in the database
    query_params = {
        "first_name": "Marco Antonio",
        "last_name_father": "Aguilar",
        "last_name_mother": "Cortes"
    }
    response = client.get('/User/search', query_string=query_params)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert all('first_name' in user for user in data)
    assert all('last_name_father' in user for user in data)
    assert all('last_name_mother' in user for user in data)

def testGetUserByNamesNotFound(client):
    """Test retrieval error when no user is found."""
    query_params = {
        "first_name": "Nonexistent",
        "last_name_father": "User",
        "last_name_mother": "Here"
    }
    response = client.get('/User/search', query_string=query_params)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No User found'

