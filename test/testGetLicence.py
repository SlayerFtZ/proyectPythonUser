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

def testGetUserByLicenseSuccess(client):
    """Test successful retrieval of user data by license."""
    license = "10315777"
    response = client.get(f'/User/{license}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'first_name' in data
    assert data['first_name'] == "Marco Antonio"
    assert 'license' in data
    assert data['license'] == license

def testGetUserByLicenseNotFound(client):
    """Test retrieval error for non-existent license."""
    license = "99999999"
    response = client.get(f'/User/{license}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'User not found'

def testGetUserByLicenseInvalidFormat(client):
    """Test retrieval error for invalid license format."""
    license = "*****"
    response = client.get(f'/User/{license}')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'License format is invalid, only numbers are allowed' 

def testGetUserByLicenseDatabaseError(client, mocker):
    """Test server error due to database connection issues."""
    mocker.patch('main.connectdataBase', return_value=None)
    
    license = "10315777"
    response = client.get(f'/User/{license}')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Database connection error'


